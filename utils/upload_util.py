import os
from data.tabular import Tabular


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
    path = os.path.join(app_root, 'user_data', username, 'datasets', dataset_name, dataset_name + '.csv')

    # Create Tabular dataset
    dataset = Tabular(dataset_name, path)  # TODO who have to create dataset

    # Check test files
    path_test = os.path.join(app_root, 'user_data', username, 'datasets', dataset_name, 'test')
    test_files = [os.path.join(path_test, f) for f in os.listdir(path_test) if os.path.isfile(os.path.join(path_test, f))]
    dataset.set_test_file(test_files)

    sess.create_helper(dataset)
    return True


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
