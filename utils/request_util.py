from flask import json


def get_json_attr(request, attr):
    try:
        return json.loads(request.form[attr])
    except:
        return request.get_json()[attr]

def default_feature(request):
    return get_json_attr(request, 'default_featu')


def get_cat_columns(request):
    return get_json_attr(request, 'cat_column')


def default_columns(request):
    return get_json_attr(request, 'default_column')


def get_selected_rows(request):
    return get_json_attr(request, 'selected_rows')


def get_percent(request):
    return ",".join([request.form['train_split'], request.form['val_split'], request.form['test_split']])


def get_action(request):
    return request.form['action']


def is_run(request):
    return get_action(request) == 'run'


def get_resume_from(request):
    return request.form['resume_from']


def get_radiob(request):
    return request.form['radiob']
