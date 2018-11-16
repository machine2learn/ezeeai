import os
from config import config_reader

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


def new_config(dataset_name, username, sess, app_root):
    sess.set_dataset_name(dataset_name)
    path = os.path.join(app_root, 'user_data', username, 'datasets', dataset_name, 'train', dataset_name + '.csv')
    sess.set_file(path)
    return True


def load_config(dataset_name, config_name, username, sess, APP_ROOT):
    path = os.path.join(APP_ROOT, 'user_data', username, dataset_name)
    sess.set_dataset_name(dataset_name)
    sess.set_config_file(os.path.join(path, config_name, 'config.ini'))
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
