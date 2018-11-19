from config import config_reader
from reader.train_csv_reader import TrainCSVReader
from reader.validation_csv_reader import ValidationCSVReader
from utils import sys_ops
import pytest
import numpy as np

import tensorflow as tf

tf.enable_eager_execution()

# CONFIG_FILE = "../config/default.ini"
CONFIG_FILE = "data_test/iris_config.ini"


@pytest.fixture
def config():
    # return config_reader.read_config(sys_ops.abs_path_of(CONFIG_FILE))
    return config_reader.read_config(CONFIG_FILE)


@pytest.fixture
def train_reader(config):
    defaults = {'sepal_length': '5.8', 'sepal_width': '3', 'petal_length': '4.35', 'petal_width': '1.3',
                'class': 'Iris-setosa'}
    dtypes = {'numerical': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'], 'categorical': ['class']}
    return TrainCSVReader(config, defaults, dtypes, 'class')


@pytest.fixture
def validation_reader(config):
    return ValidationCSVReader(config=config)


# def test_get_label_name(train_reader, validation_reader):
#     lable_name = train_reader._get_label_name()
#     assert lable_name == 'species'
#     columns = train_reader._column_names()
#     np.testing.assert_array_equal(columns, ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species'])
#
#     lable_name = validation_reader._get_label_name()
#     assert lable_name == 'species'
#     columns = validation_reader._column_names()
#     np.testing.assert_array_equal(columns, ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species'])


def test_dataset(train_reader):
    for x, y in train_reader.make_dataset_from_config({'batch_size': 128, 'num_epochs': 4}):
        print(y.shape)


def test_feature_columns(train_reader):
    a = train_reader._feature_names().values
    print(a, type(a), a.shape)
    np.testing.assert_array_equal(train_reader._feature_names(),
                                  ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])


def test_unique_values(train_reader):
    np.testing.assert_array_equal(train_reader.label_unique_values(), ['setosa', 'versicolor', 'virginica'])
