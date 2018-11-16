import os
from config import config_reader
from utils import config_ops
from shutil import copyfile
from forms.upload_form import UploadForm, UploadNewForm


def get_text(file_name):
    file = open('generator/' + file_name, 'r')
    text = file.read()
    file.close()
    return text


def get_examples():
    examples = {}
    types = ['regression', 'cluster', 'decision_tree']
    for type in types:
        examples[type] = get_text(type)
    return examples


# def existing_data(form, user_configs, username, sess, APP_ROOT):
#     dataset_name = form['exisiting_files-train_file_exist']
#     sess.set('dataset_name', dataset_name)
#     path = os.path.join(APP_ROOT, 'user_data', username, dataset_name)
#     if form['exisiting_files-configuration'] != 'new_config':
#         config_name = form['exisiting_files-configuration']
#         sess.set('config_file', os.path.join(path, config_name, 'config.ini'))
#         if sess.load_config():
#             return 'parameters'
#         return 'upload'
#     else:
#         new_config(dataset_name, username, sess, APP_ROOT, user_configs)
#         return 'slider'


# def new_config(dataset_name, username, sess, APP_ROOT,):
#     sess.set('dataset_name', dataset_name)
#     path = os.path.join(APP_ROOT, 'user_data', username, 'datasets', dataset_name)
#     config_name = config_ops.define_new_config_file(dataset_name, APP_ROOT, username, sess.get_writer())
#     sess.set('config_file', os.path.join(path, config_name, 'config.ini'))
#     if user_configs[dataset_name] and os.path.isfile(
#             os.path.join(path, user_configs[dataset_name][0], 'config.ini')):
#         reader = config_reader.read_config(os.path.join(path, user_configs[dataset_name][0], 'config.ini'))
#         copyfile(os.path.join(path, user_configs[dataset_name][0], 'config.ini'),
#                  os.path.join(path, config_name, 'config.ini'))
#         filename = reader['PATHS']['file']
#     if os.path.isfile(os.path.join(path, 'train', dataset_name + '.csv')):
#         filename = os.path.join(path, 'train', dataset_name + '.csv')
#     sess.set('file', os.path.join(path, filename))
#     sess.get_writer().add_item('PATHS', 'file', os.path.join(path, filename))
#     sess.get_writer().write_config(sess.get('config_file'))
#     return True


def new_config(dataset_name, username, sess, app_root):
    sess.set('dataset_name', dataset_name)
    path = os.path.join(app_root, 'user_data', username, 'datasets', dataset_name, 'train', dataset_name + '.csv')
    sess.set('file', path)
    return True


def load_config(dataset_name, config_name, username, sess, APP_ROOT):
    path = os.path.join(APP_ROOT, 'user_data', username, dataset_name)
    sess.set('dataset_name', dataset_name)
    sess.set('config_file', os.path.join(path, config_name, 'config.ini'))
    sess.load_config()
    reader = config_reader.read_config(os.path.join(path, config_name, 'config.ini'))
    if 'SPLIT_DF' in reader.keys():
        return reader['SPLIT_DF'].get('split_df')
    return False


def generate_dataset_name(app_root, username, dataset_name):
    user_datasets = []
    if os.path.isdir(os.path.join(app_root, 'user_data', username)):
        user_datasets = [a for a in os.listdir(os.path.join(app_root, 'user_data', username))
                         if os.path.isdir(os.path.join(app_root, 'user_data', username, a))]
    cont = 1
    while dataset_name + '_' + str(cont) in user_datasets:
        cont += 1
    new_dataset_name = dataset_name + '_' + str(cont)
    return new_dataset_name
