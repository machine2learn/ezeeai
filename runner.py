from estimator import MultOutEstimator, Estimator
from reader.train_csv_reader import TrainCSVReader, TrainCSVReaderMultOut
from reader.validation_csv_reader import ValidationCSVReader, ValidationCSVReaderMultOut
from tensorflow.python.framework.errors import InvalidArgumentError, NotFoundError
from abc import ABCMeta, abstractmethod


class AbstractRunner(metaclass=ABCMeta):

    def __init__(self, targets, config, feature_columns):
        self.targets = targets
        self.config = config
        self.feature_columns = feature_columns
        self.estimator = None
        self.create_estimator()

    @abstractmethod
    def create_estimator(self):
        pass

    def get_estimator(self):
        return self.estimator

    def run(self):
        try:
            self.get_estimator().run()
        # except tf.errors.NotFoundError:
        except (InvalidArgumentError, NotFoundError):
            self.get_estimator().clear_checkpoint()
            self.get_estimator().run()

    def predict(self, features, df, all=False):
        try:
            result = self.get_estimator().predict(features, df, all)
        except (InvalidArgumentError, NotFoundError):
            result = None
        return result

    def predict_test(self, test_file, df):
        try:
            result = self.get_estimator().predict_test(test_file, df)
        except (InvalidArgumentError, NotFoundError):
            result = None
        return result

    def explain(self, features, df, feature_types, num_features, top_labels):
        try:
            result = self.get_estimator().explain(features, df, feature_types, num_features, top_labels)

        except (InvalidArgumentError, NotFoundError):
            result = None
        return result


class Runner(AbstractRunner):
    def __init__(self, config, feature_columns, label_name, label_unique_values, default_values, dtypes):
        self.train_csv_reader = TrainCSVReader(config, default_values, dtypes, label_name)
        self.validation_csv_reader = ValidationCSVReader(config, default_values, dtypes, label_name)
        self.label_unique_values = label_unique_values
        super().__init__(label_name, config, feature_columns)

    def create_estimator(self):
        params = {
            # 'max_steps': 5000
        }
        config_params = self.config.all()
        config_params.update(params)

        config_params['canned_data'] = self.config.get_canned_data()

        self.estimator = Estimator(config_params, self.train_csv_reader, self.validation_csv_reader,
                                   self.feature_columns, self.label_unique_values)


class MultRegrRunner(AbstractRunner):
    def __init__(self, config, feature_columns, label_names, default_values, dtypes, sel_target):
        self.train_csv_reader = TrainCSVReaderMultOut(config, default_values, dtypes, label_names)
        self.validation_csv_reader = ValidationCSVReaderMultOut(config, default_values, dtypes, label_names)
        self.sel_target = sel_target
        super().__init__(label_names, config, feature_columns)

    def create_estimator(self):
        params = {
            # 'max_steps': 5000
        }
        config_params = self.config.all()
        config_params.update(params)
        config_params['canned_data'] = self.config.get_canned_data()
        self.estimator = MultOutEstimator(config_params, self.train_csv_reader, self.validation_csv_reader,
                                          self.feature_columns, self.sel_target)

