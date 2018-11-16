from pprint import pprint

import tensorflow as tf
from typing import Dict
import pandas as pd
from abc import ABCMeta, abstractmethod
import numpy as np


class CSVReader(metaclass=ABCMeta):

    def __init__(self, config, column_defaults, dtypes):
        self.config = config
        self.filename = None
        self.batch_size = None
        self.num_epochs = None
        self.label_name = None
        self.column_defaults = None
        self.keyed_column_defaults = None
        self.convert_defaults(dtypes, column_defaults)

    def make_dataset_from_config(self, params: Dict[str, object] = None) -> tf.data.Dataset:
        self._set_params(params)
        return self._make_csv_dataset(self.num_epochs)

    def convert_defaults(self, dtypes, column_defaults):
        defaults = column_defaults.copy()
        defaults.update({key: float(defaults[key]) for key in dtypes['numerical']})
        if 'range' in dtypes:
            defaults.update({key: int(float(defaults[key])) for key in dtypes['range']})

        self.column_defaults = [[key] for key in defaults.values()]
        self.keyed_column_defaults = defaults

    def make_dataset_from_file(self, params, file):
        self._set_params(params)
        self.filename = file
        return self._make_csv_dataset(self.num_epochs)

    @abstractmethod
    def _set_params(self, params: Dict[str, object]) -> None:
        pass

    def _make_csv_dataset(self, num_epo):
        dataset = tf.contrib.data.make_csv_dataset([self.filename], self.batch_size, num_epochs=num_epo,
                                                   label_name=self.label_name, column_defaults=self.column_defaults,
                                                   shuffle=False)

        # TODO perhaps no need to cast
        # dataset = dataset.map(functools.partial(parser, key='int_big_variance'))
        return dataset

    def _column_names(self) -> pd.DataFrame:
        return pd.read_csv(self.filename, nrows=2).columns

    def _feature_names(self):
        feature_slice = self.config.feature_slice()
        return self._column_names()[feature_slice]

    # def _get_label_name(self):
    #     columns = self._column_names()
    #     mask = self.config.label_slice()
    #     return columns[mask]


    # def label_unique_values(self):
    #     label_column = self._get_label_name()
    #     df = pd.read_csv(self.filename, usecols=[label_column])
    #     return df[label_column].unique()

    def clean_values(self, df):
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        for c in df.columns.values:
            df[c] = df[c].fillna(self.keyed_column_defaults[c])
            df[c] = df[c].astype(type(self.keyed_column_defaults[c]))
        return df

    def make_numpy_array(self, target, include_features=None, numerical_labels=True):
        df = self.clean_values(pd.read_csv(self.filename))
        y = df[target].values
        del df[target]
        if include_features is not None:
            df = df[include_features]
        for c in df.columns:
            if df[c].dtype == 'object':
                df[c] = df[c].astype('category')
        cat_columns = df.select_dtypes(['category']).columns
        df[cat_columns] = df[cat_columns].apply(lambda x: x.cat.codes)
        unique = np.unique(y).tolist()

        if numerical_labels: #one-hot encoding
            labels = np.zeros((len(y), len(unique)))
            for i in range(len(y)):
                labels[i][unique.index(y[i])] = 1
            labels = np.array(labels)
        else:
            labels = y
        return df.values, labels
