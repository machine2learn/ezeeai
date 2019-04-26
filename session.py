from config.config_writer import ConfigWriter
from config import config_reader

from data.tabular import Tabular as DataTabular
from data.image import Image as DataImage

from flask import session, redirect, url_for
from helper import Tabular, Image

import dill as pickle
import os
import pandas as pd


class Session:
    def __init__(self, app, appConfig):
        self._config_writer = {}
        self._config = {}
        self._app = app
        self._appConfig = appConfig
        self._helper = None

    def get_helper(self):
        return self._helper

    def set_helper(self, helper):
        self._helper = helper

    def create_helper(self, dataset):
        if isinstance(dataset, DataTabular):
            helper = Tabular(dataset, self._appConfig)
        if isinstance(dataset, DataImage):
            helper = Image(dataset, self._appConfig)
        self.set_helper(helper)

    def add_user(self, user):
        self._config[user] = {}
        self._config_writer[user] = ConfigWriter()

    def reset_user(self):
        user = self.get_session()
        self._config[user] = {}
        self._config_writer[user] = ConfigWriter()
        self._helper = None

    def get_session(self):
        with self._app.app_context():
            if 'user' not in session:
                return redirect(url_for('login'))
            return session['user'], session['_id']

    def get(self, key):
        return self.get_config()[key]

    def remove(self, key):
        if key in self.get_config():
            del self.get_config()[key]

    def set_dict_graphs(self, dict_graphs):
        self.set('dict_graphs', dict_graphs)

    def set_dict_table(self, dict_table):
        self.set('dict_table', dict_table)

    def set_new_features(self, new_features):
        self.set('new_features', new_features)

    def set_type(self, type):
        self.set('type', type)

    def get_type(self):
        return self.get('type')

    def get_dict_graphs(self):
        return self.get('dict_graphs')

    def get_dict_table(self):
        return self.get('dict_table')

    def get_new_features(self):
        return self.get('new_features')

    def get_exp_target(self):
        return self.get('exp_target')

    def set_logits(self, logits):
        self.set('logits', logits)

    def get_logits(self):
        return self.get('logits')

    def get_has_targets(self):  # TODO move to tabular
        return self.get('has_targets')

    def set_has_targets(self, has_t):
        self.set('has_targets', has_t)

    def get_predict_file(self):
        return self.get('predict_file')

    def set_predict_file(self, predict_file):
        self.set('predict_file', predict_file)

    def get_config(self):
        user = self.get_session()
        return self._config[user]

    def get_writer(self):
        user = self.get_session()
        return self._config_writer[user]

    def get_custom_path(self):
        return self.get('custom_path')

    def set_custom_path(self, c_path):
        self.set('custom_path', c_path)

    def get_transform_path(self):
        return self.get('transform_path')

    def set_transform_path(self, c_path):
        self.set('transform_path', c_path)

    def get_model_name(self):
        return self.get('model_name')

    def get_config_file(self):
        return self.get('config_file')

    def get_metric(self):
        return "Accuracy" if self.get_helper().get_mode() == "classification" else "R-squared"

    def get_status(self):
        return self.get('status')

    def set(self, key, value):
        user = self.get_session()
        self._config[user][key] = value

    def set_model_name(self, model_name):
        self.set('model_name', model_name)

    def set_mode(self, mode):
        self.set('mode', mode)

    def get_mode(self):
        return self.get('mode')

    def set_model(self, model):
        self.set('model', model)

    def get_model(self):
        return self.get('model')

    def set_canned_data(self, data):
        self.set('canned_data', data)

    def get_canned_data(self):
        return self.get('canned_data')

    def set_cy_model(self, cy_model):
        self.set('cy_model', cy_model)

    def get_cy_model(self):
        return self.get('cy_model')

    def get_y_true(self):
        return self.get('y_true')

    def get_y_pred(self):
        return self.get('y_pred')

    def set_y_true(self, y_true):
        return self.set('y_true', y_true)

    def set_y_pred(self, y_pred):
        return self.set('y_pred', y_pred)

    def fet_mdoe(self):
        return self.get('mode')

    def set_running(self):
        self.set('status', 'running')

    def set_config_file(self, config_file):
        self.set('config_file', config_file)

    def set_paused(self):
        self.set('status', 'paused')

    def set_generate_df(self, dataset_name, USER_ROOT):
        path = os.path.join(USER_ROOT, 'user_data', session['user'], 'datasets', dataset_name, dataset_name + '.csv')
        df = pd.read_csv(path)
        self.set('generated_df', df)

    def update_writer_conf(self, conf):
        user = self.get_session()
        self._config_writer[user].config = conf

    def load_config(self):
        # read saved config
        conf = config_reader.read_config(self.get('config_file'))

        # update files and df in config dict
        if 'PATHS' in conf.keys():
            dataset = pickle.load(open(conf['PATHS']['data_path'], 'rb'))
            self.create_helper(dataset)
            self.update_writer_conf(conf)
            return True
        return False

    def check_log_fp(self, all_params_config):
        logfile = os.path.join(all_params_config['PATHS']['log_dir'], 'tensorflow.log')
        try:
            self.set('log_fp', open(logfile))
        except FileNotFoundError:
            open(logfile, 'a').close()
            self.set('log_fp', open(logfile))
        try:
            self.get_status()
        except KeyError:
            self.set_paused()

    def run_or_pause(self, is_running):
        if is_running:
            self.set_running()
        else:
            self.set_paused()

    def check_key(self, key):
        return key in self.get_config()

    def set_custom(self, request):
        self.set('loss', request['loss_function'])
        self.set('model', request['model'])
        self.set('cy_model', request['cy_model'])

    def write_params(self):
        hlp = self.get_helper()  # TODO
        data_path = os.path.join(os.path.dirname(self.get_config_file()), hlp.get_dataset_name() + '.pkl')
        self.set_data_path(data_path)
        self.get_writer().add_item('PATHS', 'data_path', data_path)

        hlp.write_dataset(data_path)

        if self.get('mode') == 'custom':
            self.get_writer().add_item('CUSTOM_MODEL', 'custom_path', self.get('custom_path'))
            self.get_writer().add_item('CUSTOM_MODEL', 'transform_path', self.get('transform_path'))
            self.get_writer().add_item('CUSTOM_MODEL', 'loss_function', self.get('loss'))

        self.get_writer().write_config(self.get_config_file())

    def get_data_path(self):
        return self.get('data_path')

    def set_data_path(self, path):
        self.set('data_path', path)

    def write_config(self):
        self.get_writer().write_config(self.get_config_file())

    def mode_is_canned(self):
        return self.get_mode() == 'canned'

    def get_explain_params(self):
        return self.get('explain_params')
