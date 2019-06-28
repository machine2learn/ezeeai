import configparser
import json
import shutil

import dill as pickle
import numpy as np
import os
import pandas as pd

from ezeeai.data.utils.image import find_image_files_folder_per_class, find_image_files_from_file
from ezeeai.utils.custom import save_local_model
from ezeeai.utils.request_util import get_dataset, get_split

from . import upload_util, sys_ops
from .preprocessing import has_header
from .sys_ops import check_zip_file, unzip, tree_remove, find_dataset_from_numpy, rename, get_all_datasets, \
    get_dataset_path, get_modelname_path, get_models_path

from werkzeug.utils import secure_filename

option_map = {'option1': '.images1', 'option2': '.images2', 'option3': '.images3'}


class SavedReq:
    def __init__(self, data):
        self.data = data

    def get_json(self):
        return self.data


def get_datasets(USER_ROOT, username):
    return [x for x in get_all_datasets(USER_ROOT, username) if x[0] != '.']


def get_datasets_type(USER_ROOT, username):
    datasets = []
    for dataset in get_all_datasets(USER_ROOT, username):
        if dataset[0] == '.':
            continue
        dt_type = [x for x in os.listdir(get_dataset_path(USER_ROOT, username, dataset)) if
                   x[0] == '.']
        if len(dt_type) == 0:
            continue
        for t in dt_type:
            if 'tabular' in t:
                dt_type = 'Tabular'
            if 'image' in t:
                dt_type = 'Image'
            # dt_type = 'Tabular' if 'tabular' in dt_type[0] else 'Image'
        datasets.append([dataset, dt_type])
    return datasets


def get_datasets_and_types(USER_ROOT, username):
    data_and_type = {}
    datasets = get_datasets(USER_ROOT, username)
    for dataset in datasets:
        for entry in os.scandir(get_dataset_path(USER_ROOT, username, dataset)):
            if entry.is_file() and entry.name[0] == '.':
                data_and_type[dataset] = entry.name[1:]
    return data_and_type


def update_config_dir(config_writer, target):
    config_writer.add_item('PATHS', 'checkpoint_dir', os.path.join(target, 'checkpoints'))
    config_writer.add_item('PATHS', 'custom_model', os.path.join(target, 'custom'))
    config_writer.add_item('PATHS', 'export_dir', os.path.join(target, 'checkpoints', 'export', 'best_exporter'))
    config_writer.add_item('PATHS', 'log_dir', os.path.join(target, 'log'))
    config_writer.add_item('PATHS', 'tmp_dir', os.path.join(target, 'tmp'))


def create_model(username, USER_ROOT, model_name):
    path = get_modelname_path(USER_ROOT, username, model_name)
    os.makedirs(path, exist_ok=True)
    # sys_ops.copyfile('config/default_config.ini', path + '/config.ini')
    # return path + '/config.ini'


def define_new_model(USER_ROOT, username, config_writer, model_name):
    target = get_modelname_path(USER_ROOT, username, model_name)
    update_config_dir(config_writer, target)
    os.makedirs(target, exist_ok=True)
    os.makedirs(os.path.join(target, 'log'), exist_ok=True)
    os.makedirs(os.path.join(target, 'tmp'), exist_ok=True)
    create_model(username, USER_ROOT, model_name)
    return model_name


def get_configs_files(USER_ROOT, username, not_validated=False):
    parameters_configs = {}
    path_models = get_models_path(USER_ROOT, username)
    models = [a for a in os.listdir(path_models) if os.path.isdir(os.path.join(path_models, a))]

    if not not_validated:
        models = [m for m in models if (os.path.isfile(os.path.join(path_models, m, 'custom', 'model_tfjs.json')) or
                                        os.path.isfile(os.path.join(path_models, m, 'custom', 'canned_data.json')))]

    for model in models:
        config = configparser.ConfigParser()
        config.read(os.path.join(path_models, model, 'config.ini'))
        parameters_configs[model] = {}
        if 'BEST_MODEL' in config.sections():
            parameters_configs[model]['perf'] = config.get('BEST_MODEL', 'max_perf')
            parameters_configs[model]['loss'] = config.get('BEST_MODEL', 'min_loss')
        if 'PATHS' in config.sections():
            dataset = pickle.load(open(config.get('PATHS', 'data_path'), 'rb'))
            parameters_configs[model]['dataset'] = dataset.get_name()  # TODO from data object

    return models, parameters_configs


def new_config(train_form_file, test_form_file, USER_ROOT, username):
    ext = train_form_file.filename.split('.')[-1]
    dataset_name = train_form_file.filename.split('.' + ext)[0]
    dataset_name, path = check_dataset_path(USER_ROOT, username, dataset_name)
    sys_ops.save_filename(path, train_form_file, dataset_name)

    open(os.path.join(path, '.tabular'), 'w')

    if not isinstance(test_form_file, str):
        ext = test_form_file.filename.split('.')[-1]
        test_file = test_form_file.filename.split('.' + ext)[0]
        sys_ops.save_filename(os.path.join(path, 'test'), test_form_file, test_file)
    else:
        os.makedirs(os.path.join(path, 'test'), exist_ok=True)
    os.makedirs(os.path.join(path, 'train'), exist_ok=True)
    os.makedirs(os.path.join(path, 'valid'), exist_ok=True)
    return dataset_name


def check_dataset_path(USER_ROOT, username, dataset_name):
    path = get_dataset_path(USER_ROOT, username, dataset_name)
    if os.path.isdir(path):
        dataset_name = upload_util.generate_dataset_name(USER_ROOT, username, dataset_name)
        path = get_dataset_path(USER_ROOT, username, dataset_name)
    os.makedirs(path, exist_ok=True)
    return dataset_name, path


def new_image_dataset(USER_ROOT, username, option, file):
    if isinstance(file, str):
        return False
    dataset_name = file.filename.split('.')[0]
    dataset_name, dataset_path = check_dataset_path(USER_ROOT, username, dataset_name)

    open(os.path.join(dataset_path, option_map[option]), 'w')

    dataset_test_path = os.path.join(dataset_path, 'test')
    os.makedirs(dataset_test_path, exist_ok=True)

    train_path = os.path.join(dataset_path, 'train')
    os.makedirs(train_path, exist_ok=True)

    filename = secure_filename(file.filename)
    path_file = os.path.join(dataset_path, filename)
    file.save(path_file)

    if option == 'option3':
        try:
            train_data, test_data = find_dataset_from_numpy(path_file)
            np.savez(os.path.join(train_path, filename), x=train_data[0], y=train_data[1])
            if test_data:
                os.makedirs(os.path.join(dataset_test_path, dataset_name), exist_ok=True)
                np.savez(os.path.join(dataset_test_path, dataset_name, dataset_name + '.npz'), x=test_data[0],
                         y=test_data[1])
                open(os.path.join(dataset_test_path, dataset_name, '.option0'), 'w')  # NUMPY FILE
            return dataset_name
        except Exception as e:
            tree_remove(dataset_path)
            raise e

    if not check_zip_file(path_file):
        tree_remove(dataset_path)
        raise ValueError('Invalid file.')

    unzip(path_file, train_path)
    try:
        if option == 'option1':
            if 'train' in os.listdir(train_path):
                rename(os.path.join(train_path, 'train'), train_path)
            find_image_files_folder_per_class(train_path)
            if 'test' in os.listdir(train_path):
                dataset_test_path = os.path.join(dataset_test_path, dataset_name)
                os.makedirs(dataset_test_path, exist_ok=True)
                rename(os.path.join(train_path, 'test'), dataset_test_path)
                find_image_files_folder_per_class(dataset_test_path, require_all=False)
                open(os.path.join(dataset_test_path, '.option2'), 'w')

        elif option == 'option2':
            info_file = [f for f in os.listdir(train_path) if f.startswith('labels.') or f.startswith('train.')]
            assert len(info_file) == 1
            os.rename(os.path.join(train_path, info_file[0]), os.path.join(train_path, 'labels.txt'))
            find_image_files_from_file(train_path, os.path.join(train_path, 'labels.txt'))

            info_test_file = [f for f in os.listdir(train_path) if f.startswith('test.')]
            if len(info_test_file) == 1:
                find_image_files_from_file(train_path, os.path.join(train_path, info_test_file[0]), require_all=False)

                dataset_test_path = os.path.join(dataset_test_path, dataset_name)
                os.makedirs(dataset_test_path, exist_ok=True)

                args = {}
                if not has_header(os.path.join(train_path, info_test_file[0])):
                    args['header'] = None

                df = pd.read_csv(os.path.join(train_path, info_test_file[0]), sep=None, engine='python', **args)

                filenames = df[df.columns[0]].values
                if not os.path.isfile(filenames[0]):
                    filenames = [os.path.join(train_path, f) for f in filenames]

                for f in filenames:
                    os.rename(f, os.path.join(dataset_test_path, os.path.basename(f)))
                os.rename(os.path.join(train_path, info_test_file[0]), os.path.join(dataset_test_path, 'labels.txt'))
                open(os.path.join(dataset_test_path, '.option3'), 'w')  # NUMPY FILE

    except AssertionError as e:
        tree_remove(dataset_path)
        raise e
    return dataset_name


def default_model(local_sess, session, USER_ROOT, appConfig):
    username = session['user']
    local_sess.add_user((username, session['_id']))

    data_dir = os.path.join('ezeeai', 'default', 'iris')
    req = SavedReq(json.load(open(os.path.join(data_dir, 'req.json'))))

    dataset_name = get_dataset(req)

    dst_dir = os.path.join(USER_ROOT, username, 'datasets', dataset_name)
    shutil.copytree(data_dir, dst_dir)
    os.makedirs(os.path.join(dst_dir, 'train'), exist_ok=True)
    os.makedirs(os.path.join(dst_dir, 'valid'), exist_ok=True)
    os.makedirs(os.path.join(dst_dir, 'test'), exist_ok=True)

    from .upload_util import new_config as nconfig
    nconfig(dataset_name, username, local_sess, USER_ROOT, appConfig)
    hlp = local_sess.get_helper()
    hlp.set_split(get_split(req))
    local_sess = save_local_model(local_sess, req, USER_ROOT, username)
    define_new_model(USER_ROOT, username, local_sess.get_writer(), local_sess.get_model_name())
    local_sess.write_params()
