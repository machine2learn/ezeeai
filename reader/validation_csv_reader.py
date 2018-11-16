from reader.csv_reader import CSVReader
from typing import Dict
from make_csv_dataset import make_csv_dataset_multiple_output, make_csv_dataset


class ValidationCSVReader(CSVReader):

    def __init__(self, config: str, column_defaults: list, dtypes, label_name: str = None):
        super().__init__(config, column_defaults, dtypes)
        self.filename = self.config.validation_path()
        self.label_name = label_name
        self.num_epochs = 1

    def _set_params(self, params: Dict[str, object]) -> None:
        self.batch_size = params['validation_batch_size']


class ValidationCSVReaderMultOut(CSVReader):
    def __init__(self, config: str, column_defaults, dtypes, label_names):
        super().__init__(config, column_defaults, dtypes)
        self.filename = self.config.validation_path()
        self.label_names = label_names

    def _set_params(self, params: Dict[str, object]) -> None:
        self.batch_size = params['validation_batch_size']

    def _make_csv_dataset(self, num_epo):
        dataset = make_csv_dataset_multiple_output([self.filename], self.batch_size, num_epochs=1, shuffle=False,
                                                   label_names=self.label_names, column_defaults=self.column_defaults)
        return dataset


class TestCSVReader(CSVReader):
    def __init__(self, config: str, column_defaults: list, dtypes, label_name: str = None):
        super().__init__(config, column_defaults, dtypes)
        self.filename = self.config.validation_path()
        self.label_name = label_name
        self.num_epochs = 1


class KerasValidationCSVReader(ValidationCSVReader):
    def __init__(self, config: str, column_defaults: list, dtypes, label_name: str = None, feature_columns: list = None,
                 input_map: dict = None):
        super().__init__(config, column_defaults, dtypes, label_name)
        self.feature_columns = feature_columns
        self.input_map = input_map

    def _make_csv_dataset(self, num_epo):
        dataset = make_csv_dataset([self.filename], self.batch_size, num_epochs=num_epo,
                                   label_name=self.label_name, column_defaults=self.column_defaults,
                                   shuffle=False, feature_columns=self.feature_columns, input_name=self.input_map)
        return dataset


class KerasValidationCSVReaderMultOut(ValidationCSVReaderMultOut):
    def __init__(self, config: str, column_defaults, dtypes, label_names, feature_columns: list = None,
                 input_map: dict = None):
        super().__init__(config, column_defaults, dtypes, label_names)
        self.feature_columns = feature_columns
        self.input_map = input_map

    def _make_csv_dataset(self, num_epo):
        dataset = make_csv_dataset_multiple_output([self.filename], self.batch_size, num_epochs=1, shuffle=False,
                                                   label_names=self.label_names, column_defaults=self.column_defaults,
                                                   feature_columns=self.feature_columns, input_name=self.input_map)
        return dataset


class KerasTestCSVReader(KerasValidationCSVReader):
    def __init__(self, config: str, column_defaults: list, dtypes, label_name: str = None, feature_columns: list = None,
                 input_map: dict = None):
        super().__init__(config, column_defaults, dtypes, feature_columns=feature_columns, input_map=input_map)
        self.filename = self.config.validation_path()
        self.label_name = label_name
        self.num_epochs = 1
