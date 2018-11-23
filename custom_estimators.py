import tensorflow as tf
import tensorflow.losses
from tensorflow.python.feature_column import feature_column
from tensorflow.python.ops import lookup_ops
from tensorflowjs.converters import keras_tfjs_loader
from tensorflow.python.framework import ops
import tensorflow.keras.backend as K
from keras.utils.generic_utils import has_arg, to_list, object_list_uid, unpack_singleton

import dill as pickle

optimizer_map = {'Adagrad': tf.train.AdagradOptimizer,
                 'Adam': tf.train.AdamOptimizer,
                 'Ftrl': tf.train.FtrlOptimizer,
                 'RMSProp': tf.train.RMSPropOptimizer,
                 'SGD': tf.train.GradientDescentOptimizer}

initializers = {
    'constant': {"value": {"type": "float", "value": 0}},
    "identity": {"gain": {"type": "float", "value": 1}},
    "orthogonal": {"gain": {"type": "float", "value": 1}},
    "randomNormal": {"mean": {"type": "float", "value": 0}, "stddev": {"type": "float", "value": 1}},
    "randomUniform": {"minval": {"type": "float", "value": 0}, "maxval": {"type": "float", "value": 1}},
    "truncatedNormal": {"mean": {"type": "float", "value": 0}, "stddev": {"type": "float", "value": 1}},
    "varianceScaling": {"scale": {"type": "float", "value": 1},
                        "mode": {"type": "select", "value": 'fanIn', "options": ['fanIn', 'fanOut', 'fanAvg']},
                        "distribution": {"type": "select", "value": 'normal', "options": ['normal', 'uniform']}}}
initializers_opts = {
    "glorotNormal": "glorot_normal",
    "glorotUniform": "glorot_uniform",
    "heNormal": "he_normal",
    "identity": "identity",
    "leCunNormal": "lecun_normal",
    "ones": "ones",
    "orthogonal": "orthogonal",
    "randomNormal": "random_normal",
    "randomUniform": "random_uniform",
    "truncatedNormal": "truncated_normal",
    "varianceScaling": "variance_scaling",
    "zeros": "Zeros"}


def dic_initializer_param(initializer, params):
    for key, value in params.items():
        params[key] = float(value) if initializers[initializer][key]['type'] == 'float' else value
    return params


def get_label_ids(labels, label_vocabulary):
    if label_vocabulary is None:
        if not labels.dtype.is_integer:
            raise ValueError('Labels dtype should be integer. Instead got {}.'.
                             format(labels.dtype))
        label_ids = labels
    else:
        label_ids = lookup_ops.index_table_from_tensor(
            vocabulary_list=tuple(label_vocabulary),
            name='class_id_lookup').lookup(labels)
    return label_ids


def get_label_classes(label_ids, label_vocabulary):
    if label_vocabulary is None:
        if not label_ids.dtype.is_integer:
            raise ValueError('Labels dtype should be integer. Instead got {}.'.
                             format(label_ids.dtype))
        labels = label_ids
    else:
        table = tf.contrib.lookup.index_to_string_table_from_tensor(
            label_vocabulary, default_value="UNKNOWN")
        labels = table.lookup(label_ids)
    return labels


def create_train_op(loss, params, mode):
    assert mode == tf.estimator.ModeKeys.TRAIN

    opt = optimizer_map[params['optimizer']]
    optimizer = opt(learning_rate=params['learning_rate'])
    loss += tf.losses.get_regularization_loss()
    train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())
    return train_op


def create_output(features, params, mode):
    if 'mode' not in params:
        raise ValueError('missing mode in params')

    label_vocabulary = params['label_vocabulary'] if 'label_vocabulary' in params else None
    dataset = pickle.load(open(params['data_path'], 'rb'))

    if params['mode'] == 'custom':
        if hasattr(dataset, 'get_feature_columns'):
            features = tf.feature_column.input_layer(features, dataset.get_feature_columns())
        model = keras_tfjs_loader.load_keras_model(params['model_path'],
                                                   load_weights=False,
                                                   use_unique_name_scope=False)
        return run_internal_graph(model, features, mode), label_vocabulary
    if params['mode'] == 'canned_dnn':
        if hasattr(dataset, 'get_feature_columns'):
            features = tf.feature_column.input_layer(features, dataset.get_feature_columns())
        return dnn(features, params, mode), label_vocabulary

    if params['mode'] == 'canned_linear':
        return linear(features, params['feature_columns'], params), label_vocabulary

    raise ValueError('invalid mode ' + params['mode'] + ', should be custom or canned')


def regressor(features, labels, mode, params):
    output, _ = create_output(features, params, mode)
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode, predictions={'predictions': output})

    loss = getattr(tensorflow.losses, params['loss_function'])(tf.reshape(labels, tf.shape(output)), output)
    if mode == tf.estimator.ModeKeys.EVAL:
        axis = 0 if 'label_dimension' in params else None
        r_squared = rsquared(tf.reshape(labels, tf.shape(output)), output, axis=axis)
        metrics = {'r_squared': r_squared}
        tf.summary.scalar('r_squared', r_squared[0])
        return tf.estimator.EstimatorSpec(mode, loss=loss, eval_metric_ops=metrics,
                                          predictions={'predictions': output})

    train_op = create_train_op(loss, params, mode)

    return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)


def classifier(features, labels, mode, params):
    output, label_vocabulary = create_output(features, params, mode)
    predicted_classes = tf.argmax(output, 1)

    if mode == tf.estimator.ModeKeys.PREDICT:
        predictions = {
            'class_ids': predicted_classes[:, tf.newaxis],
            'probabilities': tf.nn.softmax(output) if 'softmax' not in output.name.lower() else output,
            'logits': output,
            'classes': get_label_classes(predicted_classes, label_vocabulary)[:, tf.newaxis]
        }
        return tf.estimator.EstimatorSpec(mode, predictions=predictions)

    label_ids = get_label_ids(labels, label_vocabulary)
    reshaped_labels = tf.reshape(label_ids, [-1, 1])
    reshaped_labels = reshaped_labels if 'sparse' in params['loss_function'] else tf.one_hot(
        tf.reshape(label_ids, [-1]),
        params['n_classes'])
    loss = getattr(tensorflow.losses, params['loss_function'])(reshaped_labels, output)

    if mode == tf.estimator.ModeKeys.EVAL:
        probs = tf.nn.softmax(output) if 'softmax' not in output.name.lower() else output
        accuracy = tf.metrics.accuracy(labels=label_ids,
                                       predictions=predicted_classes,
                                       name='accuracy')
        map = tf.metrics.average_precision_at_k(labels=label_ids,
                                                predictions=probs,
                                                k=params['n_classes'],
                                                name='mean_average_precision')

        precision = tf.metrics.precision_at_k(labels=label_ids,
                                              predictions=probs,
                                              k=params['n_classes'],
                                              name='mean_precision')
        recall = tf.metrics.recall_at_k(labels=label_ids,
                                        predictions=probs,
                                        k=params['n_classes'],
                                        name='mean_recall')
        metrics = {
            'accuracy': accuracy,
            'mean_average_precision': map,
            'mean_precision': precision,
            'mean_recall': recall
        }
        tf.summary.scalar('accuracy', accuracy[0])
        tf.summary.scalar('mean_average_precision', map[0])
        tf.summary.scalar('mean_precision', precision[0])
        tf.summary.scalar('mean_recall', recall[0])
        return tf.estimator.EstimatorSpec(mode, loss=loss, eval_metric_ops=metrics)

    train_op = create_train_op(loss, params, mode)

    return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)


def binary_classifier(features, labels, mode, params):
    output, label_vocabulary = create_output(features, params, mode)
    predicted_classes = tf.cast(output > 0.5, tf.int64)

    if mode == tf.estimator.ModeKeys.PREDICT:
        predictions = {
            'class_ids': predicted_classes[:, tf.newaxis],
            'probabilities': tf.nn.sigmoid(output) if 'sigmoid' not in output.name.lower() else output,
            'logits': output,
            'classes': get_label_classes(predicted_classes, label_vocabulary)
        }
        return tf.estimator.EstimatorSpec(mode, predictions=predictions)

    label_ids = get_label_ids(labels, label_vocabulary)
    loss = getattr(tensorflow.losses, params['loss_function'])(tf.reshape(label_ids, tf.shape(output)), output)

    if mode == tf.estimator.ModeKeys.EVAL:
        accuracy = tf.metrics.accuracy(labels=label_ids,
                                       predictions=predicted_classes,
                                       name='accuracy')
        probs = tf.nn.sigmoid(output) if 'sigmoid' not in output.name.lower() else output
        auc = tf.metrics.auc(labels=label_ids,
                             predictions=probs,
                             name='auc')
        auc_pr = tf.metrics.auc(labels=label_ids,
                                predictions=probs,
                                name='auc_precision_recall',
                                curve='PR')
        precision = tf.metrics.precision(labels=label_ids,
                                         predictions=probs,
                                         name='precision')
        recall = tf.metrics.recall(labels=label_ids,
                                   predictions=probs,
                                   name='recall')
        metrics = {
            'accuracy': accuracy,
            'auc': auc,
            'auc_precision_recall': auc_pr,
            'precision': precision,
            'recall': recall
        }
        tf.summary.scalar('accuracy', accuracy[0])
        tf.summary.scalar('auc', auc[0])
        tf.summary.scalar('auc_precision_recall', auc_pr[0])
        tf.summary.scalar('precision', precision[0])
        tf.summary.scalar('recall', recall[0])
        return tf.estimator.EstimatorSpec(mode, loss=loss, eval_metric_ops=metrics)

    train_op = create_train_op(loss, params, mode)

    return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)


def get_num_outputs(params):
    if 'label_dimension' in params:
        return params['label_dimension']
    if params['n_classes'] == 0 or params['n_classes'] == 2:
        return 1
    return params['n_classes']


def linear(features, feature_columns, params):
    return _linear(get_num_outputs(params), features, feature_columns, params['sparse_combiner'])


def dnn(net, params, mode):
    dropout = None if 'dropout' not in params else params['dropout']
    regularizer_params = {
        'scale_l1': params['l1_regularization'],
        'scale_l2': params['l2_regularization']
    }
    initializer_name = params['kernel_initializer']['name']
    kernel_initializer = None

    if 'params' in params['kernel_initializer']:
        dict_param_initializer = dic_initializer_param(initializer_name, params['kernel_initializer']['params'])

        kernel_initializer = getattr(tf.initializers, initializers_opts[initializer_name])(**dict_param_initializer)
    model = _DNNModel(get_num_outputs(params), params['hidden_units'], params['activation_fn'], dropout,
                      params['batch_norm'], kernel_regularizer_params=regularizer_params,
                      kernel_initializer=kernel_initializer)

    return model(net, mode)


def rsquared(labels, predictions, axis=None):
    SST, update_op1 = tf.metrics.mean_squared_error(labels, tf.reduce_mean(labels, axis=axis, keepdims=True))
    SSE, update_op2 = tf.metrics.mean_squared_error(labels, predictions)
    return tf.subtract(1.0, tf.div(SSE, SST)), tf.group(update_op1, update_op2)


def _get_previous_name_scope():
    current_name_scope = ops.get_name_scope()
    return current_name_scope.rsplit('/', 1)[0] + '/'


class _DNNModel(tf.keras.Model):
    def __init__(self, units, hidden_units, activation_fn, dropout, batch_norm,
                 kernel_initializer=tf.glorot_uniform_initializer(), kernel_regularizer_params=None):
        super(_DNNModel, self).__init__()
        self._dropout = dropout
        self._batch_norm = batch_norm

        self._hidden_layers = []
        self._dropout_layers = []
        self._batch_norm_layers = []
        self._hidden_layer_scope_names = []

        kernel_regularizer = None
        if kernel_regularizer_params:
            kernel_regularizer = tf.contrib.layers.l1_l2_regularizer(**kernel_regularizer_params)

        for layer_id, num_hidden_units in enumerate(hidden_units):
            with tf.variable_scope(
                    'hiddenlayer_%d' % layer_id) as hidden_layer_scope:
                hidden_layer = tf.layers.Dense(
                    units=num_hidden_units,
                    activation=activation_fn,
                    kernel_initializer=kernel_initializer,
                    kernel_regularizer=kernel_regularizer,
                    name=hidden_layer_scope,
                    _scope=hidden_layer_scope)
                self._add_layer(hidden_layer, hidden_layer_scope.name)
                self._hidden_layer_scope_names.append(hidden_layer_scope.name)
                self._hidden_layers.append(hidden_layer)
                if self._dropout is not None:
                    dropout_layer = tf.layers.Dropout(rate=self._dropout)
                    self._add_layer(dropout_layer, dropout_layer.name)
                    self._dropout_layers.append(dropout_layer)
                if self._batch_norm:
                    batch_norm_layer = tf.layers.BatchNormalization(
                        # The default momentum 0.99 actually crashes on certain
                        # problem, so here we use 0.999, which is the default of
                        # tf.contrib.layers.batch_norm.
                        momentum=0.999,
                        trainable=True,
                        name='batchnorm_%d' % layer_id,
                        _scope='batchnorm_%d' % layer_id)
                    self._add_layer(batch_norm_layer, batch_norm_layer.name)
                    self._batch_norm_layers.append(batch_norm_layer)

        with tf.variable_scope('prediction_layers') as pred_scope:
            self._prediction_layer = tf.layers.Dense(
                units=units,
                activation=None,
                kernel_initializer=kernel_initializer,
                kernel_regularizer=kernel_regularizer,
                name=pred_scope,
                _scope=pred_scope)
            self._add_layer(self._prediction_layer, pred_scope.name)
            self._pred_scope_name = pred_scope.name

    def _add_layer(self, layer, layer_name):
        setattr(self, layer_name, layer)

    def call(self, net, mode):
        is_training = mode == tf.estimator.ModeKeys.TRAIN
        # The Keras training.Model adds a name_scope with the name of the model
        # which modifies the constructed graph. Hence we add another name_scope
        # here which is the one before the training.Model one was applied.
        # TODO(rohanj): Remove this in TF 2.0 (b/116728605)
        with tf.name_scope(name=_get_previous_name_scope()):

            for i in range(len(self._hidden_layers)):
                net = self._hidden_layers[i](net)
                if self._dropout is not None and is_training:
                    net = self._dropout_layers[i](net, training=True)
                if self._batch_norm:
                    net = self._batch_norm_layers[i](net, training=is_training)

            pred = self._prediction_layer(net)
            return pred


def _linear(units, features, feature_columns, sparse_combiner='sum'):
    linear_model = feature_column._LinearModel(  # pylint: disable=protected-access
        feature_columns=feature_columns,
        units=units,
        sparse_combiner=sparse_combiner,
        name='linear_model')
    output = linear_model(features)
    return output


def run_internal_graph(model, inputs, mode, mask=None):
    """Computes output tensors for new inputs.
    # Note:
        - Expects `inputs` to be a list (potentially with 1 element).
        - Can be run on non-Keras tensors.
    # Arguments
        inputs: List of tensors
        masks: List of masks (tensors or None).
    # Returns
        Three lists: output_tensors, output_masks, output_shapes
    """
    is_training = mode == tf.estimator.ModeKeys.TRAIN
    inputs = to_list(inputs)

    if mask is None:
        masks = [None for _ in range(len(inputs))]
    else:
        masks = to_list(mask)

    cache_key = object_list_uid(inputs)
    cache_key += '_' + object_list_uid(masks)

    if cache_key in model._output_tensor_cache:
        return model._output_tensor_cache[cache_key]
    # Dictionary mapping reference tensors to tuples
    # (computed tensor, compute mask)
    # we assume a 1:1 mapping from tensor to mask
    # TODO: raise exception when a `.compute_mask()` call
    # does not return a list the same size as `call`
    tensor_map = {}
    for x, y, mask in zip(model.inputs, inputs, masks):
        tensor_map[str(id(x))] = (y, mask)

    depth_keys = list(model._nodes_by_depth.keys())
    depth_keys.sort(reverse=True)
    for depth in depth_keys:
        nodes = model._nodes_by_depth[depth]
        for node in nodes:
            # This is always a single layer, never a list.
            layer = node.outbound_layer
            reference_input_tensors = node.input_tensors
            reference_output_tensors = node.output_tensors

            # If all previous input tensors are available in tensor_map,
            # then call node.inbound_layer on them.
            computed_data = []  # List of tuples (input, mask).
            for x in reference_input_tensors:
                if str(id(x)) in tensor_map:
                    computed_data.append(tensor_map[str(id(x))])

            if len(computed_data) == len(reference_input_tensors):
                # call layer
                with K.name_scope(layer.name):
                    if node.arguments:
                        kwargs = node.arguments
                    else:
                        kwargs = {}
                    if len(computed_data) == 1:
                        computed_tensor, computed_mask = computed_data[0]
                        if has_arg(layer.call, 'mask'):
                            if 'mask' not in kwargs:
                                kwargs['mask'] = computed_mask
                        if has_arg(layer.call, 'training'):
                            kwargs['training'] = is_training
                        output_tensors = to_list(
                            layer.call(computed_tensor, **kwargs))
                        output_masks = layer.compute_mask(computed_tensor,
                                                          computed_mask)
                        if output_masks is None:
                            output_masks = [None for _ in output_tensors]
                        else:
                            output_masks = to_list(output_masks)
                        computed_tensors = [computed_tensor]

                        # computed_masks might be used in the future.
                        computed_masks = [computed_mask]
                    else:
                        computed_tensors = [x[0] for x in computed_data]
                        computed_masks = [x[1] for x in computed_data]
                        if has_arg(layer.call, 'mask'):
                            if 'mask' not in kwargs:
                                kwargs['mask'] = computed_masks
                        output_tensors = to_list(
                            layer.call(computed_tensors, **kwargs))
                        output_masks = layer.compute_mask(computed_tensors,
                                                          computed_masks)
                        if output_masks is None:
                            output_masks = [None for _ in output_tensors]
                        else:
                            output_masks = to_list(output_masks)
                    # Apply activity regularizer if any:
                    if (hasattr(layer, 'activity_regularizer') and
                            layer.activity_regularizer is not None):
                        with K.name_scope('activity_regularizer'):
                            regularization_losses = [
                                layer.activity_regularizer(x)
                                for x in output_tensors]
                        layer.add_loss(regularization_losses,
                                       inputs=computed_tensors)

                    if len(output_masks) != len(output_tensors):
                        raise Exception(
                            'Layers should have equal number of output tensors '
                            'and output masks. Layer ' + str(layer.name) + ' has'
                                                                           ' ' + str(
                                len(output_tensors)) + ' output tensors '
                                                       'and ' + str(len(output_masks)) + ' output masks.')
                # Update model updates and losses:
                # Keep track of updates that depend on the inputs
                # (e.g. BN updates).
                model.add_update(layer.get_updates_for(computed_tensors), inputs)
                # Keep track of unconditional updates (e.g. a counter).
                model.add_update(layer.get_updates_for(None), None)
                # Keep track of losses that depend on the inputs
                # (e.g. activity regularizers).
                model.add_loss(layer.get_losses_for(computed_tensors), inputs)
                # Keep track of unconditional losses
                # (e.g. weight regularizers).
                model.add_loss(layer.get_losses_for(None), None)

                # Update _keras_shape.
                if all([hasattr(x, '_keras_shape') for x in computed_tensors]):
                    input_shapes = unpack_singleton(
                        [x._keras_shape for x in computed_tensors])
                    shapes = to_list(layer.compute_output_shape(input_shapes))
                    uses_learning_phase = any(
                        [x._uses_learning_phase for x in computed_tensors])

                    for x, s in zip(output_tensors, shapes):
                        x._keras_shape = s
                        _u = getattr(x, '_uses_learning_phase', False)
                        x._uses_learning_phase = _u or uses_learning_phase

                # Update tensor_map.
                for x, y, mask in zip(reference_output_tensors,
                                      output_tensors,
                                      output_masks):
                    tensor_map[str(id(x))] = (y, mask)

    output_tensors = []
    output_masks = []
    output_shapes = []
    for x in model.outputs:
        assert str(id(x)) in tensor_map, 'Could not compute output ' + str(x)
        tensor, mask = tensor_map[str(id(x))]
        if hasattr(tensor, '_keras_shape') and output_shapes is not None:
            shape = tensor._keras_shape
            output_shapes.append(shape)
        else:
            output_shapes = None
        output_tensors.append(tensor)
        output_masks.append(mask)

    # Update cache;
    # keys are based on ids on input tensors and inputs masks.
    cache_key = object_list_uid(inputs)
    cache_key += '_' + object_list_uid(masks)

    output_tensors = unpack_singleton(output_tensors)
    model._output_tensor_cache[cache_key] = output_tensors

    output_masks = unpack_singleton(output_masks)
    model._output_mask_cache[cache_key] = output_masks

    if output_shapes is not None:
        input_shapes = [x._keras_shape for x in inputs]
        cache_key = ', '.join([str(x) for x in input_shapes])

        output_shapes = unpack_singleton(output_shapes)
        model._output_shape_cache[cache_key] = output_shapes

    return output_tensors
