from flask import json


def get_json_attr(request, attr):
    try:
        return json.loads(request.form[attr])
    except:
        return request.get_json()[attr]


def get_action(request):
    return request.form['action']


def get_all(request):
    return get_json_attr(request, 'all')


def get_cat_columns(request):
    return get_json_attr(request, 'cat_column')


def get_cy_model(request):
    return get_json_attr(request, 'cy_model')


def get_data(request):
    return get_json_attr(request, 'data')


def get_dataset(request):
    return get_json_attr(request, 'dataset')


def get_datasetname(request):
    return get_json_attr(request, 'datasetname')


def get_default_columns(request):
    return get_json_attr(request, 'default_column')


def get_default_feature(request):
    return get_json_attr(request, 'default_featu')


def get_delete_id(request):
    return get_json_attr(request, 'deleteID')


def get_filename(request):
    return get_json_attr(request, 'filename')


def get_generate_dataset_name(request):
    return request.form['generate_dataset-dataset_name']


def get_loss(request):
    return get_json_attr(request, 'loss')


def get_model(request):
    return get_json_attr(request, 'model')


def get_mode(request):
    return get_json_attr(request, 'mode')


def get_model_name(request):
    return get_json_attr(request, 'model_name')


def get_modelname(request):
    try:
        return request.form['model_name']
    except:
        return request.get_json()['model_name']


def get_models(request):
    return get_json_attr(request, 'models')


def get_normalize(request):
    return get_json_attr(request, 'normalize')


def get_num_feat(request):
    return int(request.form['num_feat'])


def get_radiob(request):
    return request.form['radiob']


def get_resume_from(request):
    return request.form['resume_from']


def get_script(request):
    return get_json_attr(request, 'script')


def get_sel_target(request):
    return request.form['exp_target']


def get_selected_rows(request):
    return get_json_attr(request, 'selected_rows')


def get_split(request):
    train = str(get_json_attr(request, 'train'))
    valid = str(get_json_attr(request, 'validation'))
    test = str(get_json_attr(request, 'test'))
    return ",".join([train, valid, test])


def get_targets(request):
    return get_json_attr(request, 'targets')


def get_top_labels(request):
    return int(request.form['top_labels'])


def is_run(request):
    return get_action(request) == 'run'
