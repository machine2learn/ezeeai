import os
import json
import shutil


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