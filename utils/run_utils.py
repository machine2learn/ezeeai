import os
import math
import json
import numpy as np
from tensorflow.python.framework.errors_impl import DataLossError, NotFoundError
from tensorflow.python.platform import gfile
from tensorflow.python.summary import summary_iterator

from config import config_reader
from utils import feature_util, request_util
import pandas as pd


def get_html_types(dict_types):
    dict_html_types = {}
    for k, v in dict_types.items():
        dict_html_types[k] = "text" if v in ['categorical', 'range'] else "number"
    return dict_html_types


def get_dictionaries(features, categories, fs, targets):
    dict_types = {}
    categoricals = {}
    cont = 0
    for k, v in features.items():
        if categories[cont] != 'none':
            dict_types[k] = categories[cont]
            if categories[cont] == 'categorical':
                categoricals[k] = fs.cat_unique_values_dict[k]
            else:
                if categories[cont] == 'range':
                    categoricals[k] = fs.df[k].unique().tolist()

        cont += 1
    for target in targets:
        if target in categoricals.keys():
            categoricals.pop(target)
    return dict_types, categoricals


def check_exports(directory):
    results = {}
    if not os.path.isfile(os.path.join(directory, 'export.log')):
        return results

    return json.load(open(os.path.join(directory, 'export.log'), 'r'))


def get_eval_results(directory, config_writer, CONFIG_FILE):
    results = {}
    if not os.path.isfile(os.path.join(directory, 'export.log')):
        return results

    log_file = json.load(open(os.path.join(directory, 'export.log'), 'r'))

    max_perf = 0
    max_perf_index = 0
    min_loss = math.inf
    min_loss_index = 0
    for k in list(log_file.keys()):
        metric = "accuracy"
        v = log_file[k]
        if not os.path.isdir(k):
            del log_file[k]
            continue
        step = str(int(v['global_step']))
        if 'accuracy' in v.keys():
            perf = v['accuracy']
        else:
            perf = v['r_squared']
            metric = 'r_squared'

        if max_perf < perf:
            max_perf = perf
            max_perf_index = step

        loss = v['average_loss'] if 'average_loss' in v else v['loss']

        if min_loss > loss:
            min_loss = loss
            min_loss_index = step
        try:
            perf = float("{0:.3f}".format(perf))
        except ValueError:
            perf = perf
        results[k.split('/')[-1]] = {metric: perf, 'loss': float("{0:.3f}".format(loss)), 'step': step}
    json.dump(log_file, open(os.path.join(directory, 'export.log'), 'w'))

    if 'TRAINING' in config_writer.config.sections():
        config_writer.add_item('BEST_MODEL', 'max_perf', str(float("{0:.3f}".format(max_perf))))
        config_writer.add_item('BEST_MODEL', 'max_perf_index', str(max_perf_index))
        config_writer.add_item('BEST_MODEL', 'min_loss', str(float("{0:.3f}".format(min_loss))))
        config_writer.add_item('BEST_MODEL', 'min_loss_index', str(min_loss_index))
        config_writer.write_config(CONFIG_FILE)
    return results


def get_predictions(targets, final_pred):
    return dict(zip(targets, final_pred.astype(str))) if len(targets) > 1 else {targets[0]: str(final_pred)}


def create_result_parameters(request, sess, default_features=False, checkpoint=None):
    if 'radiob' in request.form:
        sess.set('model', request_util.get_radiob(request))
        sess.set('exp_target', request.form['exp_target'])
    new_features = feature_util.get_new_features(request.form, sess.get_defaults(), sess.get_targets(),
                                                 sess.get_fs().group_by(sess.get_cat_list())[
                                                     'none']) if not default_features else sess.get_defaults()
    all_params_config = config_reader.read_config(sess.get_config_file())
    all_params_config.set('PATHS', 'checkpoint_dir', os.path.join(all_params_config.export_dir(),
                                                                  request_util.get_radiob(
                                                                      request) if checkpoint is None else checkpoint))
    labels = feature_util.get_target_labels(sess.get_targets(), sess.get_cat(), sess.get_fs())
    dtypes = sess.get_fs_by_cat()
    return new_features, all_params_config, labels, dtypes


def create_result_test_parameters(model, sess):
    all_params_config = config_reader.read_config(sess.get_config_file())
    all_params_config.set('PATHS', 'checkpoint_dir', os.path.join(all_params_config.export_dir(), model))
    labels = feature_util.get_target_labels(sess.get_targets(), sess.get_cat(), sess.get_fs())
    dtypes = sess.get_fs_by_cat()
    return all_params_config, labels, dtypes


def get_explain_disabled(cat_list):
    if any(k in cat_list for k in ("hash", "int-hash")):
        return 'true'
    return 'false'


def ckpt_to_table(checkpoints):
    perf = next(iter(checkpoints[next(iter(checkpoints))]))
    data = [[k, v[perf], v['loss']] for k, v in checkpoints.items()]
    columns = ["Model", perf.capitalize(), "Loss"]
    return pd.DataFrame(data, columns=columns)


def get_step(train_size, batch_size, path, file_pattern='*.ckpt-*.index'):
    full_event_file_pattern = os.path.join(path, file_pattern)
    try:
        files = gfile.Glob(os.path.join(full_event_file_pattern))
        if len(files) == 0:
            return 0

        files.sort(key=os.path.getmtime)
        event_file = files[-1]
        steps = int(event_file.split('.ckpt-')[-1].split('.')[0])
        epochs = int(np.floor((steps * batch_size) / train_size))

        return epochs
    except (FileNotFoundError, NotFoundError):
        return None
