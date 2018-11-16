from feature_selection import FeatureSelection
import pandas as pd
from utils import preprocessing
import os

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


def test_insert_data():
    data = preprocessing.insert_data(df, categories, unique_values, default_list, frequent_values2frequency,
                                     SAMPLE_DATA_SIZE)
    assert data.values.size == 45
    assert data.shape == (5, 9)
    # assert data.Category.values == categories
    # assert data.Defaults.values == [5.8, 3.0, 4.35, 1.3, 'Iris-setosa']


def test_split_train_test():
    percent = 15
    target = 'class'
    train_file , val_file = preprocessing.split_train_test(percent, file, target, df)
    assert os.path.isfile(train_file) == True
    assert os.path.isfile(val_file) == True
    os.remove(train_file)
    os.remove(val_file)

