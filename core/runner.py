import dill as pickle

from core.model.estimator import MultOutEstimator, Estimator
from tensorflow.python.framework.errors import InvalidArgumentError, NotFoundError


class Runner:
    def __init__(self, config):
        self.dataset = pickle.load(open(config.data_path(), 'rb'))

        self.config = config
        self.estimator = None
        self.create_estimator()

    def create_estimator(self):
        params = {
            # 'max_steps': 5000
        }
        config_params = self.config.all()
        config_params.update(params)
        if hasattr(self.config, 'canned_data'):
            config_params['canned_data'] = self.config.get_canned_data()

        if len(self.dataset.get_targets()) == 1:
            self.estimator = Estimator(config_params)
        else:
            self.estimator = MultOutEstimator(config_params)

    def get_estimator(self):
        return self.estimator

    def run(self):
        try:
            self.get_estimator().run()
        # except tf.errors.NotFoundError:
        except (InvalidArgumentError, NotFoundError) as err:
            if err.message.split('.')[0] != 'Restoring from checkpoint failed':
                raise err
            self.get_estimator().clear_checkpoint()
            self.get_estimator().run()

    def predict(self, features, all=False):
        try:
            return self.get_estimator().predict(features, all), True
        except (InvalidArgumentError, NotFoundError) as err:
            if err.message.split('.')[0] != 'Restoring from checkpoint failed':
                return err.message, False
            return 'Model\'s structure does not match the new parameter configuration', False
        except Exception as err:
            return str(err), False

    def predict_test(self, test_file):
        try:
            return self.get_estimator().predict_test(test_file), True
        except (InvalidArgumentError, NotFoundError) as err:
            if err.message.split('.')[0] != 'Restoring from checkpoint failed':
                return err.message, False
            return 'Model\'s structure does not match the new parameter configuration', False
        except Exception as err:
            return str(err), False

    def explain(self, params):
        try:
            if not isinstance(self.get_estimator(), MultOutEstimator):
                del params['sel_target']
            return self.get_estimator().explain(**params), True

        except (InvalidArgumentError, NotFoundError) as err:
            if err.message.split('.')[0] != 'Restoring from checkpoint failed':
                return err.message, False
            return 'Model\'s structure does not match the new parameter configuration', False
        except Exception as err:
            return str(err), False
