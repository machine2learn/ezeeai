from . import sys_ops
from . import run_utils
from .feature_util import prediction_from_df
from .param_utils import set_checkpoint_dir
from .request_util import get_modelname, get_checkpoint
from .metrics import store_predictions, get_mode_metrics

import os
import json
import math


def load_local_sess(local_sess, request, username, id, USER_ROOT):
    model_name = get_modelname(request)
    local_sess.add_user((username, id))
    config_path = sys_ops.get_config_path(USER_ROOT, username, model_name)
    local_sess.set_config_file(config_path)
    local_sess.set_model_name(model_name)
    local_sess.load_config()
    hlp = local_sess.get_helper()
    return hlp


def generate_local_sess(local_sess, request, username, id, USER_ROOT):
    hlp = load_local_sess(local_sess, request, username, id, USER_ROOT)
    all_params_config = run_utils.create_result_parameters(request, local_sess)
    return hlp, all_params_config


def check_structure(request, hlp):
    try:
        has_targets, test_filename, df_test, result = hlp.test_request(request)
        return None, has_targets, test_filename, df_test, result
    except Exception as e:
        return 'Test\'s file structure is not correct', None, None, None, None


def process_test_request(local_sess, hlp, all_params_config, username, USER_ROOT, request, th):
    model_name = get_modelname(request)
    try:
        error, has_targets, test_filename, df_test, result = check_structure(request, hlp)
        if error is not None:
            return {'error': error}
        set_checkpoint_dir(all_params_config, get_checkpoint(request))
        set_canned_data(username, model_name, USER_ROOT, all_params_config)
        final_pred, success = th.predict_test_estimator(all_params_config, test_filename)
        if not success:
            return {'error': final_pred}
        file_path, success = get_file_path(hlp, df_test, final_pred, test_filename)
        if not success:
            return {'error': file_path}

        predict_table = prediction_from_df(file_path)
        labels = hlp.get_target_labels()
        store_predictions(has_targets, local_sess, final_pred, hlp.get_df_test(df_test, has_targets))

        metrics = get_mode_metrics(has_targets, hlp.get_mode(), labels, local_sess, hlp.get_targets())
        avoidNaNs(metrics)
        return {'predict_table': predict_table, 'metrics': metrics, 'targets': hlp.get_targets()}
    except Exception as e:
        return {'predict_table': '', 'metrics': '', 'targets': '', 'error': str(e)}


def get_file_path(hlp, df_test, final_pred, test_filename):
    try:
        file_path = hlp.process_test_predict(df_test, final_pred, test_filename)
        return file_path, True
    except Exception as e:
        return str(e), False


def set_canned_data(username, modelname, USER_ROOT, all_params_config):
    canned_data = os.path.join(USER_ROOT, username, 'models', modelname, 'custom', 'canned_data.json')
    if os.path.isfile(canned_data):
        all_params_config.set_canned_data(json.load(open(canned_data)))


def avoidNaNs(d):
    for k, v in d.items():
        if isinstance(v, dict):
            avoidNaNs(v)
        if isinstance(v, list):
            for i in range(len(v)):
                if isinstance(d[k][i], float) and math.isnan(d[k][i]):
                    d[k][i] = 0.0
        if isinstance(v, float) and math.isnan(v):
            d[k] = 0.0
