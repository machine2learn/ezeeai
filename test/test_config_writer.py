from pprint import pprint

import pytest

from config.config_writer import ConfigWriter

form = {'checkpoints-checkpoint_dir': 'checkpoints',
        'checkpoints-log_dir': 'adf',
        'experiment-csrf_token': 'IjQ5NjViYzE4YmU1MTIzODkwZTk5ODJhZWNkMGVkM2E2MTJkMjExZjEi.DfgR9Q.0-I8GxtIJX-8lw5VkSELBGvJ7YU',
        'experiment-initialize_with_checkpoint': '',
        'experiment-keep_checkpoint_max': '50',
        'experiment-save_checkpoints_steps': '200',
        'experiment-save_summary_steps': '10',
        'experiment-throttle': '1',
        'network-csrf_token': 'IjQ5NjViYzE4YmU1MTIzODkwZTk5ODJhZWNkMGVkM2E2MTJkMjExZjEi.DfgR9Q.0-I8GxtIJX-8lw5VkSELBGvJ7YU',
        'network-hidden_layers': '10,5,1',
        'network-model_name': 'DNNRegressor',
        'train-batch_size': '32',
        'train-csrf_token': 'IjQ5NjViYzE4YmU1MTIzODkwZTk5ODJhZWNkMGVkM2E2MTJkMjExZjEi.DfgR9Q.0-I8GxtIJX-8lw5VkSELBGvJ7YU',
        'train-dropout': '0.0',
        'train-l1_regularization': '0.002',
        'train-l2_regularization': '0.002',
        'train-learning_rate': '0.01',
        'train-num_epochs': '100',
        'train-optimizer': ''}


@pytest.fixture
def config_writer():
    return ConfigWriter()


def test_populate_config(config_writer):
    config_writer.populate_config(form)
    from io import StringIO
    a = StringIO()
    config_writer.config.write(a)
    print(a.getvalue())
