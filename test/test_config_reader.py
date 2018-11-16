from config import config_reader
import pytest
from utils import sys_ops

CONFIG_FILE = "data_test/iris_config.ini"
CONFIG_FILE2 = "../config/default.ini"

@pytest.fixture
def config():
    return config_reader.read_config(CONFIG_FILE)

@pytest.fixture
def config2():
    return config_reader.read_config(CONFIG_FILE2)


def test_from_process(config: config_reader.CustomConfigParser):
    print(config.training())


def test_hidden_layers(config: config_reader.CustomConfigParser):
    a = config.hidden_layers()
    assert a == [9]
    assert isinstance(a, list)
    # assert a[0] == [32, 16, 16]
    # assert a[1] == [16, 8, 4]


def test_training(config: config_reader.CustomConfigParser):
    a = config.training()
    b = {'num_epochs': '100', 'batch_size': '32', 'optimizer': 'Adam', 'learning_rate': '0.01',
         'l1_regularization': '0', 'l2_regularization': '0', 'dropout': '0.0', 'activation_fn': 'relu'}
    assert a == b


def test_all(config: config_reader.CustomConfigParser):
    all = {'num_epochs': 100, 'batch_size': 32, 'optimizer': 'Adam', 'learning_rate': 0.01, 'l1_regularization': 0.0,
           'l2_regularization': 0.0, 'dropout': 0.0, 'activation_fn': 'relu', 'keep_checkpoint_max': 50,
           'save_checkpoints_steps': 20, 'save_summary_steps': 10, 'throttle': 1, 'validation_batch_size': 32,
           'hidden_layers': [9], 'model_name': 'DNNClassifier', 'checkpoint_dir': 'data_test/checkpoints/',
           'export_dir': 'data_test/best_exporter_test', 'log_dir': 'data_test/log', 'train_file': 'data_test/iris.csv',
           'file': 'data_test/iris.csv', 'validation_file': 'data_test/iris.csv', 'custom_model_path': 'None',
           'targets': ['class']}
    assert (config.all()) == all


def test_update(config: config_reader.CustomConfigParser):
    a = config.all()
    a.update({'num_epochs': 4000})
    assert a['num_epochs'] == 4000


def test_checkpoint_dir(config: config_reader.CustomConfigParser):
    checkpoints_dir = config.checkpoint_dir()
    assert checkpoints_dir.split('/')[-1] == ''
    assert checkpoints_dir.split('/')[-2] == 'checkpoints'



def test_configreader(config2: config_reader.CustomConfigParser):
    assert config2['TASK0']['type'] == 'classification'
    assert config2.get_as_slice("TASK0", "ground_truth_column") == -1


def test_all_configreader(config: config_reader.CustomConfigParser):
    assert config['NETWORK']['hidden_layers'] == '9'
    all = config.all()
    assert all['num_epochs'] == 100
    assert all['activation_fn'] == 'relu'


def test_get_task_sections(config: config_reader.CustomConfigParser):
    assert config_reader.get_task_sections(config) == {}
    config2 = config_reader.read_config("../config/default.ini")
    assert  len(config_reader.get_task_sections(config2)) == 1

