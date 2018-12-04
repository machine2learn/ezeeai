from lime import lime_tabular, lime_image
from scipy.misc import imresize
from data.image import norm_options

import numpy as np
import tensorflow as tf


class TabularExplainer:

    def __init__(self, dataset, verbose=True):

        train_dataset, training_labels = dataset.make_numpy_array(dataset.get_train_file())

        mode = dataset.get_mode()
        categorical_features, categorical_index, categorical_names = dataset.get_categorical_features()
        unique = self.label_unique_values if hasattr(self, 'label_unique_values') else None

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

            predict_input_fn = tf.estimator.inputs.numpy_input_fn(x=local_features,
                                                                  y=None, num_epochs=1, shuffle=False)
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
            predict_input_fn = tf.estimator.inputs.numpy_input_fn(x=x, y=None, num_epochs=1, shuffle=False)
            probabilities = list(model.predict(input_fn=predict_input_fn))
            return np.array([x['probabilities'] for x in probabilities])

        features = imresize(features, self._dataset.get_image_size(), interp='bilinear')
        features = features.astype(np.float32)

        features = norm_options[self._dataset.get_normalization_method()](features)

        return self._explainer.explain_instance(features, predict_fn, num_features=num_features)
