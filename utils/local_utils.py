from utils import sys_ops
from utils import run_utils
from utils.request_util import get_modelname
import os


def generate_local_sess(local_sess, request, username, id, APP_ROOT):
    model_name = get_modelname(request)
    local_sess.add_user((username, id))
    config_path = sys_ops.get_config_path(APP_ROOT, username, model_name)
    local_sess.set_config_file(config_path)
    local_sess.set_model_name(model_name)
    local_sess.load_config()
    hlp = local_sess.get_helper()
    all_params_config = run_utils.create_result_parameters(request, local_sess)
    return local_sess, hlp, all_params_config


def precess_test_request(request, hlp):
    try:
        has_targets, test_filename, df_test, result = hlp.test_request(request)
        return None, has_targets, test_filename, df_test, result
    except Exception as e:
        return 'Test\'s file structure is not correct', None, None, None, None


def set_checkpoint_dir(all_params_config, model_name):
    all_params_config.set('PATHS', 'checkpoint_dir', os.path.join(all_params_config.export_dir(), model_name))


def get_file_path(hlp, df_test, final_pred, test_filename):
    try:
        file_path = hlp.process_test_predict(df_test, final_pred, test_filename)
        return file_path, True
    except Exception as e:
        return str(e), False
