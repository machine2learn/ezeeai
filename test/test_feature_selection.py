import pandas as pd
import pytest

from data.feature_selection import FeatureSelection

numerical_col = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
categorical_col = ['class']
bool_col = []
int_col = []
hash_col = []
unique_values = {'class': ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']}
features_datatypes = ['numerical', 'numerical', 'numerical', 'numerical', 'categorical']


@pytest.fixture
def df():
    return pd.read_csv('data_test/iris.csv')


@pytest.fixture
def fs(df):
    return FeatureSelection(df)


def test_populate_features(df, fs):
    assert numerical_col == fs.numerical_columns
    assert categorical_col == fs.categorical_columns
    assert hash_col == fs.hash_columns
    assert bool_col == fs.bool_columns
    assert int_col == fs.int_columns
    assert unique_values == fs.cat_unique_values_dict
    assert fs.unique_value_size_dict == {'class': 3}


def test_group_by(fs):
    assert fs.group_by(features_datatypes) == {
        'numerical': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'], 'categorical': ['class']}


@pytest.mark.parametrize("targets, expect", [
    (['class'], 4),
    (['sepal_length', 'sepal_width'], 3),

])
def test_create_tf_features(fs, targets, expect):
    datatypes = ['numerical', 'numerical', 'numerical', 'numerical', 'categorical']
    normalize = True
    training_path = 'data_test/iris.csv'
    fs.create_tf_features(datatypes, targets, normalize, training_path)
    feature_len = len(fs.feature_columns)
    assert feature_len == expect


def test_update(fs):
    categories =  ['numerical', 'numerical', 'numerical', 'numerical', 'categorical']
    defaults = {'sepal_length': '5.8', 'sepal_width': '3.0', 'petal_length': '4.35', 'petal_width': '1.3', 'class': 'Iris-setosa'}
    assert fs.defaults != defaults
    fs.update(categories, defaults)
    assert fs.column_list == {'numerical': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'], 'bool': [], 'categorical': ['class'], 'int-range': [], 'int-hash': [], 'hash': []}
    assert fs.defaults == defaults


def test_assing_category(df, fs):
    config_file = 'data_test/iris_config.ini'
    category_list, unique_values, default_list, frequent_values2frequency = fs.assign_category(config_file, df)
    assert category_list == ['numerical', 'numerical', 'numerical', 'numerical', 'categorical']
    assert unique_values == [-1, -1, -1, -1, 3]
    assert default_list == {'sepal_length': 5.8, 'sepal_width': 3.0, 'petal_length': 4.35, 'petal_width': 1.3,
                            'class': 'Iris-setosa'}
    assert frequent_values2frequency['sepal_length'] == (5.0, 10)
    assert frequent_values2frequency['sepal_width'] == (3.0, 26)
    assert frequent_values2frequency['petal_length'] == (1.5, 14)
    assert frequent_values2frequency['petal_width'] == (0.2, 28)
    assert frequent_values2frequency['class'] in [('Iris-setosa', 50), ('Iris-versicolor', 50), ('Iris-virginica', 50)]

# def test_defaults(fs):
#     fs.populate_defaults()
#     # pprint(fs.means)
#     pprint(fs.modes)
#     pprint(fs.frequent_values)
#     # pprint(fs.defaults)
