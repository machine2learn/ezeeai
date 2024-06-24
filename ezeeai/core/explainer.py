from lime import lime_tabular, lime_image
from skimage.transform import resize
from skimage.transform import resize_local_mean
import numpy as np
import tensorflow as tf


class TabularExplainer:

    def __init__(self, dataset, verbose=True):

        train_dataset, training_labels = dataset.make_numpy_array(dataset.get_train_file())

        mode = dataset.get_mode()
        categorical_features, categorical_index, categorical_names = dataset.get_categorical_features()
        unique = dataset.get_target_labels()

        self._mode = mode
        self.dataset = dataset

        self._explainer = lime_tabular.LimeTabularExplainer(train_dataset,
                                                            feature_names=dataset.get_feature_names(),
                                                            class_names=unique,
                                                            categorical_features=categorical_index,
                                                            categorical_names=categorical_names,
                                                            training_labels=training_labels,
                                                            verbose=verbose,
                                                            mode=self._mode)

    def explain_instance(self, model, features, num_features=5, top_labels=3, sel_target=None):

        sample = self.dataset.create_feat_array(features)
        features = {k: features[k] for k in self.dataset.get_feature_names()}

        def predict_fn(x):
            x = x.reshape(-1, len(features))

            local_features = {k: x[:, i] for i, k in enumerate(features.keys())}
            local_features = self.dataset.from_array(local_features)

            predict_input_fn = tf.compat.v1.estimator.inputs.numpy_input_fn(x=local_features,
                                                                  y=None, num_epochs=1, shuffle=False)
            with tf.device('/cpu:0'):  # TODO maybe check if gpu is free
                predictions = list(model.predict(input_fn=predict_input_fn))

            if self._mode == 'classification':
                return np.array([x['probabilities'] for x in predictions])

            if sel_target:
                tidx = self.dataset.get_targets().index(sel_target)
                return np.array([x['predictions'][tidx] for x in predictions]).reshape(-1)

            return np.array([x['predictions'] for x in predictions]).reshape(-1)

        if self._mode == 'classification':
            return self._explainer.explain_instance(sample, predict_fn, num_features=num_features,
                                                    top_labels=top_labels)

        return self._explainer.explain_instance(sample, predict_fn, num_features=num_features)


class ImageExplainer:

    def __init__(self, dataset, verbose=True):
        self._dataset = dataset
        self._explainer = lime_image.LimeImageExplainer(verbose=verbose)

    def explain_instance(self, model, features, num_features=5, top_labels=3, sel_target=None):
        def predict_fn(x):
            x = x.astype(np.float32)
            if len(x.shape) == 3:
                x = x[np.newaxis, ...]
            x = np.apply_along_axis(self._dataset.normalize, 0, x)
            predict_input_fn = tf.compat.v1.estimator.inputs.numpy_input_fn(x=x, y=None, num_epochs=1, shuffle=False)
            with tf.device('/cpu:0'):  # TODO maybe check if gpu is free
                probabilities = list(model.predict(input_fn=predict_input_fn))
            return np.array([x['probabilities'] for x in probabilities])

        def predict_fn_greyscale(x):
            x = x.astype(np.float32)
            x = x.mean(axis=3).reshape(x.shape[0],x.shape[1],x.shape[2],-1)
            x = np.apply_along_axis(self._dataset.normalize, 0, x)
            predict_input_fn = tf.compat.v1.estimator.inputs.numpy_input_fn(x=x, y=None, num_epochs=1, shuffle=False)
            with tf.device('/cpu:0'):  # TODO maybe check if gpu is free
                probabilities = list(model.predict(input_fn=predict_input_fn))
            return np.array([x['probabilities'] for x in probabilities])

        #OLD:features = resize(features, self._dataset.get_image_size(), interp='bilinear')
        explainer_size = self._dataset.get_image_size().copy()
        explainer_size[2] = features.shape[2]
        features = resize_local_mean(features, explainer_size, preserve_range=True)

        if self._dataset.get_image_size()[2] == 1:  # 1 greyscale channel 
            predictor = predict_fn_greyscale
        else:
            predictor = predict_fn
      

        explain_result = self._explainer.explain_instance(features, predictor, batch_size=100,
                                                          num_features=num_features,
                                                          labels=self._dataset.get_class_names(),
                                                          top_labels=len(self._dataset.get_class_names()))

        features = features.astype(np.float32)

        if self._dataset.get_image_size()[2] == 1:  # 1 greyscale channel 
            features = features.mean(axis=2).reshape(features.shape[0],features.shape[1],-1)

        features = self._dataset.normalize(features)

        predict_input_fn = tf.compat.v1.estimator.inputs.numpy_input_fn(x=features[np.newaxis, ...], y=None, num_epochs=1,
                                                              shuffle=False)
        with tf.device('/cpu:0'):  # TODO maybe check if gpu is free
            predictions = list(model.predict(input_fn=predict_input_fn))

        return explain_result, predictions[0]['probabilities']
