import tensorflow as tf

from custom_estimators import regressor, classifier, binary_classifier


class ModelBuilder:

    def get_model(self, params):
        if 'label_dimension' in params or params['n_classes'] == 0:
            return regressor
        if params['n_classes'] > 2:
            return classifier
        return binary_classifier

    def create_from_canned(self, params):
        params['mode'] = 'canned_dnn' if 'hidden_units' in params else 'canned_linear'
        params['loss_function'] = params['loss_function_canned']
        model_fn = self.get_model(params)
        return tf.estimator.Estimator(model_fn=model_fn, params=params, config=params['config'],
                                      model_dir=params['checkpoint_dir'])

    def create_from_keras(self, params):
        params['mode'] = 'custom'

        model_fn = self.get_model(params)
        return tf.estimator.Estimator(model_fn=model_fn, params=params, config=params['config'],
                                      model_dir=params['checkpoint_dir'])
