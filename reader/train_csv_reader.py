from reader.csv_reader import CSVReader
from typing import Dict

from make_csv_dataset import make_csv_dataset_multiple_output
import pandas as pd
import numpy as np


class TrainCSVReader(CSVReader):

    def __init__(self, config: str, column_defaults, dtypes, label_name):
        super().__init__(config, column_defaults, dtypes)
        self.filename = self.config.training_path()
        self.label_name = label_name

    def _set_params(self, params: Dict[str, object]) -> None:
        self.batch_size = params['batch_size']
        self.num_epochs = params['num_epochs']


class TrainCSVReaderMultOut(CSVReader):

    def __init__(self, config: str, column_defaults, dtypes, label_names):
        super().__init__(config, column_defaults, dtypes)
        self.filename = self.config.training_path()
        self.label_names = label_names

    def _set_params(self, params: Dict[str, object]) -> None:
        self.batch_size = params['batch_size']
        self.num_epochs = params['num_epochs']

    def _make_csv_dataset(self, num_epo):
        dataset = make_csv_dataset_multiple_output([self.filename], self.batch_size, num_epochs=num_epo,
                                                   label_names=self.label_names, column_defaults=self.column_defaults)
        return dataset

    def make_numpy_array(self, targets, sel_target, include_features=None, numerical_labels=True):
        df = self.clean_values(pd.read_csv(self.filename))
        y = df[sel_target].values
        df.drop(targets, axis=1, inplace=True)
        if include_features is not None:
            df = df[include_features]
        for c in df.columns:
            if df[c].dtype == 'object':
                df[c] = df[c].astype('category')
        cat_columns = df.select_dtypes(['category']).columns
        df[cat_columns] = df[cat_columns].apply(lambda x: x.cat.codes)

        unique_len = len(y)

        if numerical_labels:  # one-hot encoding
            labels = (np.arange(unique_len) == y[:, None]).astype(np.float32)
        else:
            labels = y
        return df.values, labels
