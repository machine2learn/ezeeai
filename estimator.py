from abc import ABCMeta, abstractmethod

import tensorflow as tf
import shutil
import numpy as np
import logging
import os

import pandas as pd

from model_builder import ModelBuilder
from best_exporter import BestExporter
from explainer import Explainer
from utils.email_ops import send_email
from utils.run_utils import check_exports
from utils import feature_util
from utils.db_ops import get_email

HIDDEN_LAYERS = 'hidden_layers'

MAX_STEPS = 'max_steps'

KEEP_CHECKPOINT_MAX = 'keep_checkpoint_max'

SAVE_SUMMARY_STEPS = 'save_summary_steps'

SAVE_CHECKPOINTS_STEPS = 'save_checkpoints_steps'

optimizer_map = {'Adagrad': tf.train.AdagradOptimizer,
                 'Adam': tf.train.AdamOptimizer,
                 'Ftrl': tf.train.FtrlOptimizer,
                 'RMSProp': tf.train.RMSPropOptimizer,
                 'SGD': tf.train.GradientDescentOptimizer}



class AbstractEstimator(metaclass=ABCMeta):
    def __init__(self, params, train_csv_reader, validation_csv_reader, feature_columns):
        self.params = params
        self.targets = params['targets']
        self.checkpoint_dir = params['checkpoint_dir']
        self.train_csv_reader = train_csv_reader
        self.validation_csv_reader = validation_csv_reader
        self.feature_columns = feature_columns
        self.feature_names = feature_util.get_feature_names(feature_columns)
        self.model = None
        self.max_steps = np.ceil(int(params["train_size"]) / int(params["batch_size"])) * int(params["num_epochs"])
        self.test_file = ''

        tf.logging.set_verbosity(tf.logging.DEBUG)
        log = logging.getLogger('tensorflow')
        log.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(message)s')

        # create file handler which logs even debug messages
        fh = logging.FileHandler(os.path.join(params['log_dir'], 'tensorflow.log'))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        log.addHandler(fh)

        tf.reset_default_graph()
        if len(check_exports(params['export_dir'])) == 0:
            self.clear_checkpoint()

        self._create_run_config()
        self._create_model()
        self._create_specs()

    def _create_run_config(self):
        save_checkpoints_steps = self.params[SAVE_CHECKPOINTS_STEPS]
        save_summary_steps = self.params[SAVE_SUMMARY_STEPS]
        keep_checkpoint_max = self.params[KEEP_CHECKPOINT_MAX]
        self.runConfig = tf.estimator.RunConfig(model_dir=self.checkpoint_dir,
                                                save_checkpoints_steps=save_checkpoints_steps,
                                                save_summary_steps=save_summary_steps,
                                                keep_checkpoint_max=keep_checkpoint_max)

    def _create_model(self):
        mb = ModelBuilder()
        self.params['config'] = self.runConfig

        # TODO CANNED
        # self.params['hidden_units'] = self.params[HIDDEN_LAYERS]
        # self.params['activation_fn'] = getattr(tf.nn, self.params['activation_fn'])
        # self.params['batch_norm'] = self.params['batch_norm'] == 'True'

        # if self.params['gui_editor'] == 'True':
        if 'canned_data' in self.params:
            # self.params['hidden_units'] = self.params['canned_data']['hidden_layers']
            # self.params['activation_fn'] = self.params['canned_data']['activation_fn']
            # self.params['batch_norm'] = self.params['canned_data']['batch_norm']
            # self.params['dropout'] = self.params['canned_data']['dropout']
            # self.params['l1_regularization'] = self.params['canned_data']['l1_regularization']
            # self.params['l2_regularization'] = self.params['canned_data']['l2_regularization']
            # # self.params['kernel_initializer'] = self.params['canned_data']['kernel_initializer']
            # self.params['loss_function_canned'] = self.params['canned_data']['loss_function']
            self.model = mb.create_from_canned(self.feature_columns, self.params)
        else:
            self.params['model_path'] = os.path.join(self.params['custom_path'], 'model_tfjs.json')
            self.model = mb.create_from_keras(self.feature_columns, self.params)
        # else:
        #

    def _serving_input_receiver_fn(self, feature_columns):
        feature_spec = tf.feature_column.make_parse_example_spec(feature_columns)
        receiver_tensors = {k: tf.placeholder(v.dtype, [None, 1]) for k, v in feature_spec.items()}
        features = {"x": tf.concat([v for v in receiver_tensors.values()], axis=1)}
        return tf.estimator.export.ServingInputReceiver(receiver_tensors=receiver_tensors, features=features)

    def _create_specs(self):
        self.train_spec = tf.estimator.TrainSpec(
            input_fn=self._train_input_fn, max_steps=self.max_steps)

        def serving_input_receiver_fn():
            feature_spec = tf.feature_column.make_parse_example_spec(self.feature_columns)
            receiver_tensors = {k: tf.placeholder(v.dtype, [None, 1]) for k, v in feature_spec.items()}
            return tf.estimator.export.ServingInputReceiver(receiver_tensors=receiver_tensors,
                                                            features=receiver_tensors)

        self.eval_spec = tf.estimator.EvalSpec(
            input_fn=self._validation_input_fn,
            steps=None,  # How many batches of test data
            exporters=BestExporter(serving_input_receiver_fn=serving_input_receiver_fn,
                                   exports_to_keep=self.params[KEEP_CHECKPOINT_MAX]),
            start_delay_secs=0, throttle_secs=1)

    def _train_input_fn(self):
        return self.train_csv_reader.make_dataset_from_config(self.params)

    def _validation_input_fn(self):
        return self.validation_csv_reader.make_dataset_from_config(self.params)

    def clear_checkpoint(self):
        shutil.rmtree(self.checkpoint_dir, ignore_errors=True)

    def _test_input_fn(self):
        return self.validation_csv_reader.make_dataset_from_file(self.params, self.test_file)

    def predict_test(self, test_file, df):
        self.test_file = test_file
        dict_results = {}
        predictions = list(self.model.predict(input_fn=self._test_input_fn))
        if 'predictions' in predictions[0].keys():
            preds = [x['predictions'][0] for x in predictions]
            dict_results['preds'] = preds
            return dict_results
        dict_results['preds'] = [x['classes'][0].decode("utf-8") for x in predictions]
        dict_results['logits'] = [x['logits'] for x in predictions]
        dict_results['scores'] = [x['probabilities'] for x in predictions]
        return dict_results

    def run(self):
        tf.estimator.train_and_evaluate(self.model, self.train_spec, self.eval_spec)
        self.email = self.params['email']
        server_info = {"login": "tf3deep",
                       "password": "tf3Deep123",
                       "email_address": "tf3deep@gmail.com"}

        send_email({"email_address": self.email}, server_info)
        # send_email({"email_address": "yoel@machine2learn.nl"}, server_info)

    def _to_array(self, features, feature_types, df):
        for c in df.columns:
            if c in features.keys():
                if df[c].dtype == 'object':
                    if feature_types[c] == 'hash':
                        try:
                            features[c] = int(float(features[c]))
                        except:
                            pass
                    df[c] = df[c].astype('category')
                    mapp = {y: x for x, y in dict(enumerate(df[c].cat.categories)).items()}
                    features[c] = float(mapp[features[c]])
                else:
                    features[c] = float(features[c])
        feats = df[self.feature_names].append(pd.DataFrame(pd.Series(features)).transpose()).tail(1)
        input_predict = feats.values.reshape(-1)
        return input_predict

    def _from_array(self, features, feature_types, df):
        for c in df.columns:
            if c in features.keys():
                if df[c].dtype == 'object':
                    df[c] = df[c].astype('category')
                    mapp = {x: y for x, y in dict(enumerate(df[c].cat.categories)).items()}
                    features[c] = np.vectorize(mapp.get)(features[c])
                    if feature_types[c] == 'hash':
                        features[c] = features[c].astype(str)
                else:
                    features[c] = features[c].astype(df[c].dtype)
        return features

    def input_predict_fn(self, features, df):
        input_predict = {}
        for k, v in features.items():
            input_predict[k] = np.array([v]).astype(df[k].dtype) if df[k].dtype == 'object' else np.array(
                [float(v)]).astype(df[k].dtype)
        # input_predict.pop(target, None)
        return input_predict


class Estimator(AbstractEstimator):

    def __init__(self, params, train_csv_reader, validation_csv_reader, feature_columns, label_unique_values):

        self.label_unique_values = label_unique_values
        super().__init__(params, train_csv_reader, validation_csv_reader, feature_columns)

    def _create_explainer(self, features, df, target_type):
        features = {k: features[k] for k in self.feature_names}
        df = df[self.feature_names]
        feature_names = df.columns.values
        train_dataset, training_labels = self.train_csv_reader.make_numpy_array(self.train_csv_reader.label_name,
                                                                                include_features=self.feature_names,
                                                                                numerical_labels=False)

        mode = 'regression' if target_type == 'numerical' else 'classification'
        categorical_features = feature_util.get_categorical_features(df, self.feature_columns)
        categorical_index = [list(df.columns.values).index(x) for x in categorical_features]
        categorical_names = {k: df[k].unique() for k in categorical_features}

        return Explainer(train_dataset, training_labels, feature_names, self.label_unique_values, categorical_index,
                         categorical_names, mode)

    def explain(self, features, df, feature_types, num_features, top_labels):
        del features[self.targets[0]]
        features = {k: features[k] for k in self.feature_names}
        target = self.targets[0]

        feat_array = self._to_array(features, feature_types, df.copy())

        explainer = self._create_explainer(features, df, feature_types[target])

        def model_predict(x):
            x = x.reshape(-1, len(features))

            local_features = {k: x[:, i] for i, k in enumerate(features.keys())}
            local_features = self._from_array(local_features, feature_types, df.copy())

            predict_input_fn = tf.estimator.inputs.numpy_input_fn(x=local_features,
                                                                  y=None, num_epochs=1, shuffle=False)
            predictions = list(self.model.predict(input_fn=predict_input_fn))
            if explainer.get_mode() == 'classification':
                probs = np.array([x['probabilities'] for x in predictions])
                return probs
            else:
                preds = np.array([x['predictions'] for x in predictions]).reshape(-1)
                return preds

        return explainer.explain_instance(feat_array, model_predict, num_features, top_labels)

    def predict(self, features, df, all=False):
        del features[self.targets[0]]
        features = {k: features[k] for k in self.feature_names}
        predict_input_fn = tf.estimator.inputs.numpy_input_fn(x=self.input_predict_fn(features, df),
                                                              y=None, num_epochs=1, shuffle=False)
        predictions = list(self.model.predict(input_fn=predict_input_fn))
        if all:
            return predictions
        if 'predictions' in predictions[0].keys():
            return predictions[0]['predictions'][0]
        return predictions[0]['classes'][0].decode("utf-8")

    def _create_model(self):
        self.params['n_classes'] = len(self.label_unique_values) if self.label_unique_values is not None else 0
        self.params['label_vocabulary'] = self.label_unique_values
        super()._create_model()


class MultOutEstimator(AbstractEstimator):

    def __init__(self, params, train_csv_reader, validation_csv_reader, feature_columns, sel_target):
        super().__init__(params, train_csv_reader, validation_csv_reader, feature_columns)
        self.sel_target = sel_target

    def _create_explainer(self, features, df):
        # feature_names = list(features.keys())
        train_dataset, training_labels = self.train_csv_reader.make_numpy_array(self.train_csv_reader.label_names,
                                                                                self.sel_target,
                                                                                include_features=self.feature_names,
                                                                                numerical_labels=False)

        df = df[self.feature_names]
        categorical_features = feature_util.get_categorical_features(df, self.feature_columns)
        categorical_index = [list(df.columns.values).index(x) for x in categorical_features]
        mode = 'regression'
        categorical_names = {k: df[k].unique() for k in categorical_features}
        return Explainer(train_dataset, training_labels, self.feature_names, None, categorical_index,
                         categorical_names, mode)

    def explain(self, features, df, feature_types, num_features, top_labels):
        self._del_target_columns(features)
        features = {k: features[k] for k in self.feature_names}

        feat_array = self._to_array(features, feature_types, df.copy())

        explainer = self._create_explainer(features, df)

        def model_predict(x):
            x = x.reshape(-1, len(features))

            local_features = {k: x[:, i] for i, k in enumerate(features.keys())}
            local_features = self._from_array(local_features, feature_types, df.copy())

            predict_input_fn = tf.estimator.inputs.numpy_input_fn(x=local_features,
                                                                  y=None, num_epochs=1, shuffle=False)
            predictions = list(self.model.predict(input_fn=predict_input_fn))
            tidx = self.targets.index(self.sel_target)

            preds = np.array([x['predictions'][tidx] for x in predictions]).reshape(-1)
            return preds

        return explainer.explain_instance(feat_array, model_predict, num_features, top_labels)

    def predict(self, features, df, all=False):
        self._del_target_columns(features)
        features = {k: features[k] for k in self.feature_names}

        predict_input_fn = tf.estimator.inputs.numpy_input_fn(x=self.input_predict_fn(features, df),
                                                              y=None, num_epochs=1, shuffle=False)
        predictions = list(self.model.predict(input_fn=predict_input_fn))

        if all:
            return predictions

        return predictions[0]['predictions']

    def predict_test(self, test_file, df):
        self.test_file = test_file
        dict_results = {}
        predictions = list(self.model.predict(input_fn=self._test_input_fn))
        dict_results['preds'] = [x['predictions'] for x in predictions]
        return dict_results

    def _del_target_columns(self, features):
        for target in self.targets:
            if target in features:
                del features[target]

    def _create_model(self):
        self.params['label_dimension'] = len(self.targets)
        super()._create_model()
