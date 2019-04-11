import configparser
from typing import Dict
from utils import sys_ops

NETWORK = "NETWORK"

EXPERIMENT = 'EXPERIMENT'

CUSTOM_MODEL = 'CUSTOM_MODEL'

TRAINING = 'TRAINING'

PATHS = 'PATHS'


class CustomConfigParser(configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_as_slice(self, *args, **kwargs):
        raw_get = self.get(*args, **kwargs)
        if ":" in raw_get:
            return slice(*map(int, raw_get.split(":")))
        else:
            return int(raw_get)

    def get_rel_path(self, *args, **kwargs):
        raw_get = self.get(*args, **kwargs)
        if not raw_get:
            return ""
        if raw_get.startswith('/'):
            return raw_get
        return sys_ops.abs_path_of(raw_get)

    def _from_training(self, param):
        return self.get(TRAINING, param)

    def _from_network(self, param):
        return self.get(NETWORK, param)

    def _from_custom(self, param):
        return self.get(CUSTOM_MODEL, param)

    def _from_process(self, param):
        return dict(self.items(EXPERIMENT, param))

    def _from_paths(self, param):
        return self[PATHS][param]

    def custom_model_path(self) -> Dict[str, str]:
        return dict(self.items(CUSTOM_MODEL))

    def training(self) -> Dict[str, str]:
        # print(self.items(TRAINING))
        return dict(self.items(TRAINING))

    def experiment(self) -> Dict[str, str]:
        return dict(self.items(EXPERIMENT))

    def path(self):
        return dict(self.items(PATHS))

    def train_batch_size(self) -> int:
        return int(self._from_training('batch_size'))

    def learning_rate(self) -> float:
        return float(self._from_training('learning_rate'))

    def optimizer(self) -> str:
        return self._from_training('optimizer')

    def num_epochs(self) -> int:
        return int(self._from_training('num_epochs'))

    def hidden_layers(self):
        return [int(x) for x in self.get('NETWORK', 'hidden_layers').split(',')]

    def hidden_canned_layers(self):
        return [int(x) for x in self.canned_data['hidden_layers']['value'].strip('[').strip(']').split(',')]

    def checkpoint_dir(self):
        return self.get_rel_path(PATHS, 'checkpoint_dir')

    def tmp_dir(self):
        return self.get_rel_path(PATHS, 'tmp_dir')

    def custom_path(self):
        return self.get_rel_path(CUSTOM_MODEL, 'custom_path')

    def batch_size(self):
        return int(self.get(TRAINING, 'batch_size'))

    def export_dir(self):
        return self.get_rel_path(PATHS, 'export_dir')

    def data_path(self):
        return self.get_rel_path(PATHS, 'data_path')

    def all(self):
        result = dict(self.items(TRAINING))
        # result.update(dict(self.items(TRAINING_ADVANCED)))
        result.update(self.items(EXPERIMENT))
        # result.update(self.items(NETWORK))
        result.update(self.items(PATHS))
        if self.has_section(CUSTOM_MODEL):
            result.update(self.items(CUSTOM_MODEL))

        int_columns = ["num_epochs", "batch_size", "validation_batch_size", "save_summary_steps",
                       "keep_checkpoint_max", "throttle", "save_checkpoints_steps"]
        float_columns = ["learning_rate"]
        # float_columns = ["learning_rate", "l1_regularization", "l2_regularization", "dropout"]

        for key in int_columns:
            if key in result:
                result[key] = int(result[key])

        for key in float_columns:
            if key in result:
                result[key] = float(result[key])

        if hasattr(self, 'canned_data'):
            if 'hidden_layers' in self.canned_data:
                result.update({'hidden_units': self.hidden_canned_layers()})

                result['activation_fn'] = self.canned_data['activation_fn']['value']
                result['batch_norm'] = self.canned_data['batch_norm']['value']
                result['dropout'] = float(self.canned_data['dropout']['value'])
                result['l1_regularization'] = float(self.canned_data['l1_regularization']['value'])
                result['l2_regularization'] = float(self.canned_data['l2_regularization']['value'])
                result['kernel_initializer'] = {'name': self.canned_data['kernel_initializer']['value']}
                if 'config' in self.canned_data['kernel_initializer'].keys():
                    result['kernel_initializer']['params'] = self.canned_data['kernel_initializer']['config']
            else:
                result['sparse_combiner'] = self.canned_data['sparse_combiner']['value']

            result['loss_function_canned'] = self.canned_data['loss_function']
        return result

    def set_canned_data(self, data):
        self.canned_data = data

    def get_canned_data(self):
        return self.canned_data

    def set_email(self, mail):
        self.set('PATHS', 'email', mail)


def read_config(path):
    config = CustomConfigParser(inline_comment_prefixes=['#'], interpolation=configparser.ExtendedInterpolation())
    config.read(path)
    return config


def get_task_sections(config):
    return {section_name: config[section_name] for section_name in config.sections() if
            section_name.startswith("TASK")}

# config = read_config("config/default.ini")
# print(config.get_slice("FEATURES","columns"))
# print ([1,2,3][config.get_slice("FEATURES","columns")])
