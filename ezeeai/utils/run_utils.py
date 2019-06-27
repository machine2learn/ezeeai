import os
import math
import json

import numpy as np
import pandas as pd

from tensorflow.python.framework.errors_impl import NotFoundError
from tensorflow.python.platform import gfile

from ..config import config_reader

from . import request_util, db_ops
from .metrics import train_eval_graphs
from .param_utils import set_form, set_checkpoint_dir
from .request_util import is_run
from .sys_ops import get_config_path, get_canned_data, get_log_mess, get_log_path


def define_empty_run_params():
    model_name = ''
    checkpoints = ''
    metric = ''
    graphs = {}
    log_mess = None
    return model_name, checkpoints, metric, graphs, log_mess

# def get_run_results(config_file, sess, username, USER_ROOT):
#     model_name = config_file.split('/')[-2]
#     sess.set_model_name(model_name)
#     export_dir = config_reader.read_config(sess.get_config_file()).export_dir()
#     checkpoints = get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
#     metric = sess.get_metric()
#     graphs = train_eval_graphs(config_reader.read_config(sess.get_config_file()).checkpoint_dir())
#     log_mess = get_log_mess(USER_ROOT, username, model_name)
#     return checkpoints, metric, graphs, log_mess


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


def create_result_parameters(request, sess, checkpoint=None):
    all_params_config = config_reader.read_config(sess.get_config_file())
    try:
        rb = request_util.get_radiob(request) if checkpoint is None else checkpoint
    except:
        rb = request.get_json()['checkpoint']
    set_checkpoint_dir(all_params_config, rb)
    return all_params_config


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
        # print(steps, epochs)
        return epochs
    except (FileNotFoundError, NotFoundError):
        return None


def run_post(sess, request, USER_ROOT, username, th):
    sess.run_or_pause(is_run(request))
    model_name = request.form['model_name']
    config_path = get_config_path(USER_ROOT, username, model_name)
    sess.set_model_name(model_name)

    sess.set_config_file(config_path)
    sess.load_config()

    sess.get_writer().populate_config(request.form)
    sess.get_writer().write_config(sess.get_config_file())

    th.run_tensor_board(username, sess.get_config_file())

    all_params_config = config_reader.read_config(sess.get_config_file())
    get_canned_data(USER_ROOT, username, model_name, all_params_config)
    all_params_config.set_email(db_ops.get_email(username))
    sess.check_log_fp(all_params_config)
    return all_params_config


def load_run_config(sess, th, username, form, USER_ROOT):
    model_name, checkpoints, metric, graphs, log_mess = define_empty_run_params()
    running, config_file = th.check_running(username)

    if not running:
        config_file = sess.get_config_file() if sess.check_key('config_file') else None

    if config_file is not None and os.path.isfile(config_file):
        sess.set_config_file(config_file)
        sess.load_config()
        set_form(form, sess.get_config_file())
        model_name = config_file.split('/')[-2]
        sess.set_model_name(model_name)
        export_dir = config_reader.read_config(sess.get_config_file()).export_dir()
        checkpoints = get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
        metric = sess.get_metric()
        graphs = train_eval_graphs(config_reader.read_config(sess.get_config_file()).checkpoint_dir())

        log_path = get_log_path(USER_ROOT, username, model_name)
        log_mess = open(log_path, 'r').read() if os.path.isfile(log_path) else ''

    return running, model_name, checkpoints, metric, graphs, log_mess
