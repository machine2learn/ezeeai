import os
import json
import dill as pkl
from utils.feature_util import save_scalers
from collections import OrderedDict


# def save_model_config(df, targets, loss, model, all_params_config, writer, config_file, cy_model, datatypes):
#     path = all_params_config.checkpoint_dir().split('checkpoints')[0]
#     custom_path = os.path.join(path, 'custom')
#     transform_path = os.path.join(path, 'transform')
#
#     writer.add_item('CUSTOM_MODEL', 'loss_function', loss)
#     writer.add_item('CUSTOM_MODEL', 'custom_path', custom_path)
#     writer.add_item('CUSTOM_MODEL', 'transform_path', transform_path)
#
#     os.makedirs(custom_path, exist_ok=True)
#     os.makedirs(transform_path, exist_ok=True)
#
#     with open(os.path.join(custom_path, 'model_tfjs.json'), 'w') as outfile:
#         json.dump(model, outfile)
#
#     with open(os.path.join(custom_path, 'model_cy.json'), 'w') as outfile:
#         json.dump(cy_model, outfile,  sort_keys=False,  separators=(',', ':'))
#
#     try:
#         # model = keras_tfjs_loader.load_keras_model(os.path.join(custom_path, 'model.json'), load_weights=False,
#         # use_unique_name_scope=True)
#         # writer.add_item("CUSTOM_MODEL", "input_map", "input1")
#         #
#         # with open(os.path.join(custom_path, 'model.json'), 'w') as outfile:
#         # json.dump(model.to_json(), outfile)
#
#         scalers = save_scalers(df, targets, datatypes)
#         pkl.dump(scalers, open(os.path.join(transform_path, "scalers.pkl"), "wb"))
#
#         writer.write_config(config_file)
#
#     except Exception as e:
#         return 'Failed to load model: ' + str(e)
#     return 'ok'


def save_model_config(df, targets, model, path, cy_model, datatypes, model_name):
    custom_path = os.path.join(path, model_name, 'custom')
    transform_path = os.path.join(path, model_name, 'transform')
    os.makedirs(custom_path, exist_ok=True)
    os.makedirs(transform_path, exist_ok=True)
    save_cy_model(custom_path, cy_model)
    with open(os.path.join(custom_path, 'model_tfjs.json'), 'w') as outfile:
        json.dump(model, outfile)

    try:
        scalers = save_scalers(df, targets, datatypes)
        pkl.dump(scalers, open(os.path.join(transform_path, "scalers.pkl"), "wb"))

    except Exception as e:
        return 'Failed to load model: ' + str(e)
    return custom_path, transform_path


def save_cy_model(custom_path, cy_model):
    os.makedirs(custom_path, exist_ok=True)
    with open(os.path.join(custom_path, 'model_cy.json'), 'w') as outfile:
        json.dump(cy_model, outfile, sort_keys=False, separators=(',', ':'))
