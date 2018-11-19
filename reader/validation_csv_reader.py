from reader.csv_reader import CSVReader
from typing import Dict
from make_csv_dataset import make_csv_dataset_multiple_output


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
