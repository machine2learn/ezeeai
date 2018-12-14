import os
import socket
import zipfile

from tensorflow.python.platform import gfile
from contextlib import closing
from werkzeug.utils import secure_filename
from pathlib import Path
import shutil

from collections import OrderedDict
from utils import preprocessing
from io import StringIO
import numpy as np
import json


def tree_remove(path):
    shutil.rmtree(path)


def zipdir(path, ziph, base):
    for root, dirs, files in os.walk(path):
        for file in files:
            src_path = os.path.join(root, file)
            base_path = base + src_path.split(base)[-1]
            ziph.write(src_path, base_path)


def check_zip_file(path_file):
    with open(path_file, 'rb') as fp:
        if not zipfile.is_zipfile(fp):
            return False
        return True


def check_numpy_file(path_file):
    try:
        data = np.load(path_file)
        # assert isinstance(data, (list, tuple, np.ndarray)) and len(data) == 2
        x, y = data['x'], data['y']

        assert len(x.shape) == 3 or len(x.shape) == 4
        assert len(y.shape) == 1 or len(y.shape) == 2

        assert x.shape[0] == y.shape[0]
        return True
    except:
        return False


def unzip(path_to_zip_file, directory_to_extract_to):
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()

    dirs = [f for f in os.listdir(directory_to_extract_to) if os.path.isdir(os.path.join(directory_to_extract_to, f))]
    filtered_dir = dirs.copy()
    for d in dirs:
        if d.startswith('__'):
            tree_remove(os.path.join(directory_to_extract_to, d))
            del filtered_dir[filtered_dir.index(d)]

    if len(filtered_dir) == 1:
        source = os.path.join(directory_to_extract_to, filtered_dir[0])
        dest1 = directory_to_extract_to

        files = os.listdir(source)
        for f in files:
            shutil.move(os.path.join(source, f), dest1)
        os.removedirs(source)


def mkdir_recursive(path):
    if not path:
        return
    sub_path = os.path.dirname(path)
    if not os.path.exists(sub_path):
        mkdir_recursive(sub_path)
    if not os.path.exists(path):
        os.mkdir(path)


def delete_recursive(paths, export_dir):
    if os.path.isdir(export_dir):
        for p in paths:
            if os.path.exists(os.path.join(export_dir, p)):  gfile.DeleteRecursively(os.path.join(export_dir, p))


def copyfile(src, dst):
    """Copy the contents (no metadata) of the file named src to a file named dst"""
    from shutil import copyfile
    if os.path.exists(src): copyfile(src, dst)


def abs_path_of(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('0.0.0.0', 0))
        return str(s.getsockname()[1])


def save_filename(target, dataset_form_field, dataset_name):
    dataset_form_field.filename = dataset_name + '.csv'
    dataset_file = dataset_form_field
    if dataset_file:
        dataset_filename = secure_filename(os.path.basename(dataset_file.filename))
        destination = os.path.join(target, dataset_filename)
        if not os.path.exists(target):
            os.makedirs(target)
        dataset_file.save(destination)
        preprocessing.clean_field_names(destination)
    return True


def bytestr2df(str_file, filename):
    data = StringIO(str_file)
    return preprocessing.clean_field_names_df(data, filename)


def change_checkpoints(config, resume_from):
    rdir = os.path.join(config.get('PATHS', 'export_dir'), resume_from)
    cdir = config.get('PATHS', 'checkpoint_dir')

    for p in Path(cdir).glob("model.*"):
        p.unlink()

    for p in Path(rdir).glob("model.*"):
        shutil.copy(p, os.path.join(cdir, p.name))

    shutil.copy(os.path.join(rdir, 'checkpoint'), os.path.join(cdir, 'checkpoint'))


def delete_models(all, models, username):
    path = os.path.join('user_data', username, 'models')
    paths = [os.path.join(path, m) for m in models]
    if all:
        paths = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    for path in paths:
        shutil.rmtree(path)


def delete_dataset(all, dataset, models, username):
    p = os.path.join('user_data', username, 'datasets')
    if all:
        paths = [os.path.join(p, d) for d in os.listdir(p)]
        delete_models(True, models, username)
    else:
        paths = [os.path.join(p, dataset)]
        delete_models(False, models, username)

    for path in paths:
        if '.DS_Store' not in path:
            shutil.rmtree(path)


def check_df(test_df, df, targets, filename):
    if not np.array_equal(test_df.columns.values, df.columns.values):
        temp_df = df.drop(columns=targets)
        if not np.array_equal(test_df.columns.values, temp_df.columns.values):
            raise ValueError("Invalid file content.")
        else:
            test_df = test_df.reindex(columns=df.columns.values)
            test_df.to_csv(filename, index=False)
            return False
    return True


def save_results(df, result, targets, filename, base_path):
    if len(targets) == 1:
        df['prediction-' + targets[0]] = result
    else:
        result = np.array(result)
        for i in range(len(targets)):
            df['prediction-' + targets[i]] = result[:, i]
    os.makedirs(os.path.join(base_path, 'predictions'), exist_ok=True)
    predict_file = os.path.join(base_path, 'predictions', filename)
    df.to_csv(predict_file, index=False)
    return predict_file


def save_image_results(test_labels, result, targets, filenames, base_path):
    predictions = []
    if len(targets) == 1:
        if test_labels is None:
            predictions.append('file,prediction')
            for f, r in zip(filenames, result):
                predictions.append('%s,%s' % (f.replace(base_path, ''), r))
        else:
            predictions.append('file,%s,prediction' % targets[0])
            for f, r, t in zip(filenames, result, test_labels[targets[0]]):
                predictions.append('%s,%s,%s' % (f.replace(base_path, ''), t, r))
    # TODO multiple classes
    base_path = base_path.replace('train', 'predictions')
    os.makedirs(base_path, exist_ok=True)
    predict_file = os.path.join(base_path, 'prediction.txt')
    with open(predict_file, 'w') as f:
        for item in predictions:
            f.write("%s\n" % item)
    return predict_file


def export_models(export_dir, selected_rows, model_name):
    model_name = model_name.strip().replace(" ", "_")
    tmp_dir = os.path.join(export_dir, model_name)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    os.makedirs(tmp_dir, exist_ok=True)
    for i in range(len(selected_rows)):
        c = selected_rows[i]
        shutil.copytree(os.path.join(export_dir, c), os.path.join(tmp_dir, str(i + 1)))

    file_path = os.path.join(export_dir, 'deployment.zip')

    zipf = zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED)
    zipdir(tmp_dir, zipf, model_name)

    dep_file = 'deployment.sh'
    with open(dep_file) as fp:
        data = fp.read()

    data = data.replace('model_name', model_name)

    with open(os.path.join(export_dir, dep_file), 'w') as fp:
        fp.write(data)

    zipf.write(os.path.join(export_dir, dep_file), dep_file)

    zipf.close()
    shutil.rmtree(tmp_dir)

    return file_path


def gen_example(targets, data, df, model_name, pred):
    feat_keys = [x for x in df.drop(targets, axis=1).columns.values]
    dtypes = [x for x in df[feat_keys].dtypes]
    example = {}

    for i in range(len(feat_keys)):
        if df[feat_keys[i]].dtype != 'object':
            example[feat_keys[i]] = np.array([float(data['Defaults'][feat_keys[i]])]).astype(dtypes[i]).tolist()
        else:
            example[feat_keys[i]] = np.array([data['Defaults'][feat_keys[i]]]).astype(dtypes[i]).tolist()

    d = {
        "signature_name": "predict",
        "instances": [example]
    }
    call = 'DOCKER_HOST=\"...\"\n'
    call += 'MODEL_NAME=\"...\"\n'
    call += 'curl -X POST http://${DOCKER_HOST}:8501/v1/models/${MODEL_NAME}/versions/1' ':predict -d '

    call += '\'' + str(d) + '\''

    pred[0] = {k: v.tolist() for k, v in pred[0].items()}
    if 'classes' in pred[0]:
        pred[0]['classes'] = pred[0]['classes'][0].decode("utf-8")
    epred = {'predictions': pred}

    return call, d, epred


def load_cy_model(model, user):
    custom_path = os.path.join('user_data', user, 'models', model, 'custom', 'model_cy.json')
    cy_model = 'None'
    if os.path.isfile(custom_path):
        cy_model = json.load(open(custom_path), object_pairs_hook=OrderedDict)
    return cy_model


def create_custom_path(APP_ROOT, username, model_name):
    path = os.path.join(APP_ROOT, 'user_data', username, 'models', model_name, 'custom')
    os.makedirs(path, exist_ok=True)
    return path


def get_config_path(APP_ROOT, username, model_name):
    return os.path.join(APP_ROOT, 'user_data', username, 'models', model_name, 'config.ini')


def get_dataset_path(APP_ROOT, username, dataset_name):
    return os.path.join(APP_ROOT, 'user_data', username, 'datasets', dataset_name)


def get_models_pat(APP_ROOT, username):
    return os.path.join(APP_ROOT, 'user_data', username, 'models')


def create_split_folders(main_path):
    os.makedirs(os.path.join(main_path, 'train'), exist_ok=True)
    os.makedirs(os.path.join(main_path, 'valid'), exist_ok=True)
    os.makedirs(os.path.join(main_path, 'test'), exist_ok=True)
