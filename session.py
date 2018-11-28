from config.config_writer import ConfigWriter
from config import config_reader
from flask import session, redirect, url_for
from helper import Tabular, Image

import dill as pickle
import os
import pandas as pd
from data.tabular import Tabular as DataTabular
from data.image import Image as DataImage

SAMPLE_DATA_SIZE = 5


class Session:
    def __init__(self, app):
        self._config_writer = {}
        self._config = {}
        # self._processes = {}
        # self._ports = {}
        self._app = app
        self._helper = None

    def get_helper(self):
        return self._helper

    def set_helper(self, helper):
        self._helper = helper

    def create_helper(self, dataset):
        if isinstance(dataset, DataTabular):
            helper = Tabular(dataset)
        if isinstance(dataset, DataImage):
            helper = Image(dataset)
        self.set_helper(helper)

    def add_user(self, user):
        self._config[user] = {}
        self._config_writer[user] = ConfigWriter()

    def reset_user(self):
        user = self.get_session()
        self._config[user] = {}
        self._config_writer[user] = ConfigWriter()

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

    # def set_test_file(self, test_file):
    #     self.set('test_file', test_file)
    #
    # def get_test_file(self):
    #     return self.get('test_file')

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

    # def set_dataset_name(self, dataset_name):
    #     self.set('dataset_name', dataset_name)
    #
    # def set_file(self, path):
    #     self.set('file', path)
    #
    # def get_dataset_name(self):
    #     return self.get('dataset_name')

    def get_custom_path(self):
        return self.get('custom_path')

    def set_custom_path(self, c_path):
        self.set('custom_path', c_path)

    def get_transform_path(self):
        return self.get('transform_path')

    def set_transform_path(self, c_path):
        self.set('transform_path', c_path)

    # def get_features(self):
    #     return self.get('features')
    #
    # def get_all_features(self):
    #     return self.get('all_features')
    #
    # def get_defaults(self):
    #     return self.get('defaults')
    #
    # def get_df(self):
    #     return self.get('df')
    #
    # def get_fs(self):
    #     return self.get('fs')
    #
    # def get_split_df(self):
    #     return self.get('split_df')

    # def get_cat(self):
    #     return self.get('data').Category
    #
    # def get_cat_list(self):
    #     return self.get('category_list')
    #
    # def get_keys(self):
    #     return self.get('df').keys()
    #
    # def get_data(self):
    #     return self.get('data')

    def get_model_name(self):
        return self.get('model_name')

    # def set_normalize(self, is_normalize):
    #     self.set('normalize', is_normalize)
    #
    # def get_normalize(self):
    #     return self.get('normalize')
    #
    # def get_train_file(self):
    #     return self.get('train_file')
    #
    # def get_targets(self):
    #     return self.get('targets')

    def get_config_file(self):
        return self.get('config_file')

    #
    # def get_file(self):
    #     return self.get('file')

    # def get_type(self):
    #     if self.get_cat()[self.get_targets()[0]] == 'numerical':
    #         return "regression"
    #     return "classification"

    def get_metric(self):
        return "Accuracy" if self.get_helper().get_mode() == "classification" else "R-squared"

    # def get_dataset_name(self):
    #     return self.get('dataset_name')

    def get_status(self):
        return self.get('status')

    # def get_fs_by_cat(self):
    #     return self.get_fs().group_by(self.get_cat_list())

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

    # def get_column_categories(self):
    #     return self.get('column_categories')
    #
    # def set_column_categories(self, column_categories):
    #     return self.set('column_categories', column_categories)

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

    # def set_split_df(self, percent):
    #     self.set('split_df', percent)

    # def set_feat_eng(self, feat_eng):
    #     self.get_writer().add_item('FEAT_ENG', 'normalize', feat_eng)

    # def set_train_size(self):
    #     self.get_writer().add_item('TRAINING', "train_size", str(self.get("train_size")))
    #
    # def set_train_size_from_pd(self):
    #     self.set("train_size", len(pd.read_csv(self.get("train_file"))))

    # def get_train_size(self):
    #     return self.get('train_size')

    def set_generate_df(self, dataset_name, APP_ROOT):
        path = os.path.join(APP_ROOT, 'user_data', session['user'], 'datasets', dataset_name, dataset_name + '.csv')
        df = pd.read_csv(path)
        self.set('generated_df', df)

    # def set_category_list(self, category_list):
    #     self.set('category_list', category_list)
    #
    # def set_targets(self, targets, normalize, training_path):
    #     self.get_writer().add_item('TARGETS', 'targets', ",".join(targets))
    #     self.set('features',
    #              self.get('fs').create_tf_features(self.get('category_list'), targets, normalize, training_path))
    #     self.set('all_features',
    #              self.get('fs').create_tf_features(self.get('category_list'), targets, normalize, training_path,
    #                                                without_label=False))
    #     self.set('targets', targets)
    #     if len(targets) == 1:
    #         target_type = self.get('data').Category[self.get('targets')[0]]
    #         if target_type == 'range':
    #             new_categ_list = []
    #             for categ, feature in zip(self.get('category_list'), self.get('df').columns):
    #                 new_categ_list.append(categ if feature != targets[0] else 'categorical')
    #             self.set('category_list', new_categ_list)
    #             self.get('data').Category = self.get('category_list')
    #             self.get('fs').update(self.get('category_list'),
    #                                   dict(zip(self.get('data').index.tolist(), self.get('data').Defaults)))

    def update_writer_conf(self, conf):
        user = self.get_session()
        self._config_writer[user].config = conf

    # def update_split(self, train_file, validation_file, test_file):
    #     self.set('train_file', train_file)
    #     self.set('validation_file', validation_file)
    #     self.remove('test_file')
    #     self.get_writer().add_item('PATHS', 'train_file', train_file)
    #     self.get_writer().add_item('PATHS', 'validation_file', validation_file)
    #     self.get_writer().add_item('SPLIT_DF', 'split_df', self.get('split_df'))
    #     if test_file != "":
    #         self.set('test_file', test_file)
    #         self.get_writer().add_item('PATHS', 'test_file', test_file)
    #         self.get_writer()
    #
    #
    # def update_new_features(self, cat_columns, default_values):
    #     self.set('category_list', cat_columns)
    #     for i in range(len(cat_columns)):
    #         if 'none' in cat_columns[i]:
    #             cat_columns[i] = 'none'
    #     self.get('data').Category = self.get('category_list')
    #     default_values = [str(v) for v in default_values]
    #     self.get('data').Defaults = default_values
    #     self.set('defaults', dict(zip(self.get('data').index.tolist(), default_values)))
    #     self.get('fs').update(self.get('category_list'), dict(zip(self.get('data').index.tolist(), default_values)))

    def load_config(self):
        # read saved config
        conf = config_reader.read_config(self.get('config_file'))  # TODO read tabular dataset
        # update files and df in config dict
        if 'PATHS' in conf.keys():
            dataset = pickle.load(open(conf['PATHS']['data_path'], 'rb'))
            self.create_helper(dataset)

            # self.set_dataset(pickle.load(open(conf['PATHS']['data_path'], 'rb')))
            # self.set('file', conf['PATHS']['file'])
            # self.set('train_file', conf['PATHS']['train_file'])
            # self.set('validation_file', conf['PATHS']['validation_file'])
            # if 'test_file' in conf['PATHS']:
            #     self.set('test_file', conf['PATHS']['test_file'])
            # self.set('df', pd.read_csv(conf['PATHS']['file']))
            # self.set('normalize', bool(conf['FEAT_ENG']['normalize'] == 'True'))
            # self.load_features()
            # # target select
            # targets = conf.targets()
            # category_list = [conf.get('COLUMN_CATEGORIES', key) for key in self.get_df().columns]
            # self.update_new_features(category_list, list(self.get('defaults').values()))
            # self.set_targets(targets, self.get('normalize'), self.get('train_file'))
            #
            # self.update_writer_conf(conf)
            return True
        return False

    # def assign_category(self, df, from_config=False):
    #     fs = FeatureSelection(df)
    #     self.set('fs', fs)
    #     category_list, unique_values, default_list, frequent_values2frequency = fs.assign_category(self.get('config_file'), df)
    #     return category_list, unique_values, default_list, frequent_values2frequency
    # def assign_category(self, df):
    #     fs = FeatureSelection(df)
    #     self.set('fs', fs)
    #     category_list, unique_values, default_list, frequent_values2frequency = fs.assign_category(df)
    #     return category_list, unique_values, default_list, frequent_values2frequency

    # def load_features(self):
    #     # retrieve values from config, assign_category does this
    #     self.set('df', pd.read_csv(self.get('file')))
    #     df = self.get('df')
    #     df.reset_index(inplace=True, drop=True)
    #     categories, unique_values, default_list, frequent_values2frequency = self.assign_category(df)
    #     default_values = [str(v) for v in default_list.values()]
    #     self.set('data',
    #              preprocessing.insert_data(df, categories, unique_values, default_list, frequent_values2frequency,
    #                                        SAMPLE_DATA_SIZE))
    #     self.set('defaults', dict(zip(self.get('data').index.tolist(), default_values)))
    #     self.set('category_list', categories)
    #     return categories

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

    # def add_cat_columns(self):
    #     for x, y in self.get_config()['column_categories'].items():
    #         self.get_writer().add_item('COLUMN_CATEGORIES', x, y)

    def write_params(self):
        hlp = self.get_helper()  # TODO revisar
        data_path = os.path.join(os.path.dirname(self.get_config_file()), hlp.get_dataset_name() + '.pkl')
        self.set_data_path(data_path)
        self.get_writer().add_item('PATHS', 'data_path', data_path)
        # self.get_writer().write_config(self.get('config_file'))

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

    # def create_data(self, dataset_name, file):
    #     tb = Tabular(dataset_name, file)
    #     self.set_dataset(tb)
