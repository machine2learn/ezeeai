from utils import feature_util
import pytest
from data.feature_selection import FeatureSelection
import pandas as pd
from config.config_writer import ConfigWriter
from config import config_reader
from utils import preprocessing

file = 'data_test/iris.csv'
config_test_file = 'data_test/iris_config_test.ini'
df = pd.read_csv('data_test/iris.csv')
fs = FeatureSelection(df)
df_range = pd.read_csv('data_test/dataset.csv')
fs_range = FeatureSelection(df_range)

categories = ['numerical', 'numerical', 'numerical', 'numerical', 'categorical']
unique_values = [-1, -1, -1, -1, 3]
default_list = {'sepal_length': 5.8, 'sepal_width': 3.0, 'petal_length': 4.35, 'petal_width': 1.3,
                'class': 'Iris-setosa'}
frequent_values2frequency = {'sepal_length': (5.0, 10), 'sepal_width': (3.0, 26), 'petal_length': (1.5, 14),
                             'petal_width': (0.2, 28), 'class': ('Iris-setosa', 50)}
SAMPLE_DATA_SIZE = 5
data = preprocessing.insert_data(df, categories, unique_values, default_list, frequent_values2frequency,
                                 SAMPLE_DATA_SIZE)
data.Category = categories


def test_already_order_reorder_request():
    features = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'class']
    categories = ['numerical', 'numerical', 'numerical', 'numerical', 'categorical']
    defaults = ['5.8', '3', '4.35', '1.3', 'Iris-setosa']
    list_features = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'class']
    new_categories, new_defaults = feature_util.reorder_request(features, categories, defaults, list_features)
    assert categories == new_categories
    assert defaults == new_defaults


def test_disorder_reorder_request():
    features = ['sepal_length', 'petal_length', 'petal_width', 'class', 'sepal_width']
    categories = ['numerical', 'numerical', 'numerical', 'categorical', 'numerical']
    defaults = ['5.8', '4.35', '1.3', 'Iris-setosa', '3']
    list_features = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'class']
    new_categories, new_defaults = feature_util.reorder_request(features, categories, defaults, list_features)
    assert ['numerical', 'numerical', 'numerical', 'numerical', 'categorical'] == new_categories
    assert ['5.8', '3', '4.35', '1.3', 'Iris-setosa'] == new_defaults


@pytest.mark.parametrize("targets", [
    (['class']),
    (['sepal_length', 'sepal_width', 'petal_length'])
])
def test_remove_targets(targets):
    features = {'sepal_length': '5.8', 'sepal_width': '3', 'petal_length': '4.35', 'petal_width': '1.3',
                'class': 'Iris-setosa'}
    new_features = feature_util.remove_targets(features, targets)
    for target in targets:
        assert target not in new_features.keys()


@pytest.mark.parametrize("targets, expect", [
    (['class'], {'sepal_length': '5.8', 'sepal_width': '3', 'petal_length': '4.35', 'petal_width': '1.3'}),
    (['sepal_length', 'sepal_width', 'petal_length'], {'petal_width': '1.3', 'class': 'Iris-setosa'}),
    (['classfasdfad'],
     {'sepal_length': '5.8', 'sepal_width': '3', 'petal_length': '4.35', 'petal_width': '1.3', 'class': 'Iris-setosa'})
])
def test_remove_target_out_of_range(targets, expect):
    features = {'sepal_length': '5.8', 'sepal_width': '3', 'petal_length': '4.35', 'petal_width': '1.3',
                'class': 'Iris-setosa'}
    assert feature_util.remove_targets(features, targets) == expect


def test_write_features():
    old_categories = ['none-numerical', 'numerical', 'numerical', 'numerical', 'categorical']
    writer = ConfigWriter()
    writer.append_config(config_test_file)
    data.Category = ['none', 'none', 'numerical', 'numerical', 'none']
    feature_util.write_features(old_categories, data, writer, config_test_file)
    reader = config_reader.read_config(config_test_file)
    assert reader['COLUMN_CATEGORIES']['sepal_length'] == 'none-numerical'
    assert reader['COLUMN_CATEGORIES']['sepal_width'] == 'none-numerical'
    assert reader['COLUMN_CATEGORIES']['petal_length'] == 'numerical'
    assert reader['COLUMN_CATEGORIES']['class'] == 'none-categorical'


@pytest.mark.parametrize("targets,  fs, expect", [
    #(['class'],  fs, ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']),
    # (['class'], fs, None),
    (['sepal_width'],  fs, None),
    (['sepal_width', 'petal_length'],  fs, None)
])
def test_get_target_labels_if_categorical(targets, fs, expect):
    target_labels = feature_util.get_target_labels(targets, data.Category, fs)
    assert target_labels == expect


@pytest.mark.parametrize("targets,  expect", [
    (['class'],  True),
    (['sepal_width'],  True),
    (['sepal_width', 'petal_length'], True),
    (['class', 'petal_length'], False),
])
def test_check_targets(targets, expect):
    feature_types = {'sepal_length': 'numerical', 'sepal_width': 'numerical', 'petal_length': 'numerical', 'petal_width': 'numerical',
                'class': 'categorical'}
    assert expect == feature_util.check_targets(feature_types, targets)