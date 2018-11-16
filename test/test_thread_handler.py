from session import Session
import flask
from user import User
from dfweb import app
from config import config_reader
import pytest
from thread_handler import ThreadHandler
from utils import feature_util, preprocessing
from utils import feature_util
import pytest
from feature_selection import FeatureSelection
import pandas as pd
from config.config_writer import ConfigWriter
from config import config_reader
from utils import preprocessing, sys_ops
import logging


def logAssert(test, msg):
    if not test:
        logging.error(msg)
        assert test, msg

def test_log(log_info):
    logging.info("testing foo")
    logAssert( log_info == 'foo', "foo is not foo")

t = ThreadHandler()
username = 'usertest'
config_file = 'data_test/iris_config.ini'
port = '5000'
target = 'class'
file = 'data_test/iris.csv'
config_test_file = 'data_test/iris_config_test.ini'
df = pd.read_csv('data_test/iris.csv')
fs = FeatureSelection(df)

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

labels = feature_util.get_target_labels(target, data.Category[target], fs)
all_params_config = config_reader.read_config(config_file)
export_dir = all_params_config.export_dir()
dtypes = fs.group_by(categories)
category_list = ['numerical', 'numerical', 'numerical', 'numerical', 'categorical']
features = fs.create_tf_features(categories, target)


def test_add_and_get_port():
    t.add_port(username, config_file, port)
    assert t.get_port(username, config_file) == port


def test_pause_threads():
    t.pause_threads(username)


# def test_run_tensor_board():
#     t.run_tensor_board(username, config_file)

def test_run_thread():
    logging.basicConfig(filename='config_check.log', level=logging.INFO)
    logging.info('start')
    # t.run_thread(all_params_config, features, target, labels, default_list, dtypes)
    logging.info('done')

# def test_tensor_board_thread():
#     config_file = '/Users/aracelicanadas/Desktop/tf3/tf3/test/data_test/best_exporter_test/1532434574/checkpoints'
#     port = sys_ops.find_free_port()
#     t.tensor_board_thread(config_file, port)
#     import urllib
#     urllib.urlopen("localhost:"+port).getcode()
