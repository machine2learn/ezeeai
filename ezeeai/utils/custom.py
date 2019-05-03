import os
import json
import shutil
from .sys_ops import get_config_path, create_custom_path, get_models_path
from .request_util import get_mode, get_cy_model, get_data, get_loss, get_model_name


def save_model_config(model, path, cy_model, model_name):
    custom_path = os.path.join(path, model_name, 'custom')
    shutil.rmtree(custom_path, ignore_errors=True)
    transform_path = os.path.join(path, model_name, 'transform')
    os.makedirs(custom_path, exist_ok=True)
    os.makedirs(transform_path, exist_ok=True)
    save_cy_model(custom_path, cy_model)
    with open(os.path.join(custom_path, 'model_tfjs.json'), 'w') as outfile:
        json.dump(model, outfile)
    return custom_path, transform_path


def save_cy_model(custom_path, cy_model):
    os.makedirs(custom_path, exist_ok=True)
    with open(os.path.join(custom_path, 'model_cy.json'), 'w') as outfile:
        json.dump(cy_model, outfile, sort_keys=False, separators=(',', ':'))


def save_canned_data(data, path):
    with open(os.path.join(path, 'canned_data.json'), 'w') as outfile:
        json.dump(data, outfile)


def save_local_model(local_sess, request, USER_ROOT, username):
    h = local_sess.get_helper()
    h.process_features_request(request)
    h.process_targets_request(request)

    model_name = get_model_name(request)
    local_sess.set_model_name(model_name)
    local_sess.set_mode(get_mode(request))

    if get_mode(request) == 'custom':
        local_sess.set_custom(request.get_json())
        path = get_models_path(USER_ROOT, username)
        os.makedirs(path, exist_ok=True)
        c_path, t_path = save_model_config(local_sess.get_model(), path, local_sess.get_cy_model(), model_name)
        local_sess.set_custom_path(c_path)  #
        local_sess.set_transform_path(t_path)
    else:
        custom_path = create_custom_path(USER_ROOT, username, model_name)
        cy_model = get_cy_model(request)
        save_cy_model(custom_path, cy_model)

        data = get_data(request)
        data['loss_function'] = get_loss(request)
        save_canned_data(data, custom_path)

        local_sess.set_canned_data(data)
        local_sess.set_cy_model(cy_model)

    config_path = get_config_path(USER_ROOT, username, local_sess.get_model_name())
    local_sess.set_config_file(config_path)
    local_sess.write_config()
    return local_sess
