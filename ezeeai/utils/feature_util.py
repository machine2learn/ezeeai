import json
import os
import pandas as pd
from .sys_ops import get_dataset_path
from .visualize_util import get_norm_corr
from tensorflow.python.feature_column.feature_column import _IndicatorColumn

SUMMARY = 'summary.json'
DATA_GRAPH = 'data_graphs.json'


def reorder_request(features, categories, defaults, list_features):
    dict_features = {}
    for f, c, d in zip(features, categories, defaults):
        dict_features[f] = {'category': c, 'default': d}
    cat_columns = [dict_features[c]['category'] for c in list_features]
    default_values = [dict_features[c]['default'] for c in list_features]
    return cat_columns, default_values


def remove_targets(features, targets):
    sfeatures = features.copy()
    for target in targets:
        if target in features.keys():
            sfeatures.pop(target)
    return sfeatures
    # raise ValueError('Target not in features')


def to_int_categories(df, target=None):
    if target is not None:
        del df[target]
    for c in df.columns:
        if df[c].dtype == 'object':
            df[c] = df[c].astype('category')
    cat_columns = df.select_dtypes(['category']).columns
    df[cat_columns] = df[cat_columns].apply(lambda x: x.cat.codes)

    return df


def drop_columns(df, feature_columns, targets):
    cols = []
    for x in feature_columns:
        if type(x) == _IndicatorColumn:
            cols.append(x[0].key)
        else:
            cols.append(x.key)
    return df[cols + targets]


def get_feature_names(feature_columns):
    cols = []
    for x in feature_columns:
        if type(x) == _IndicatorColumn:
            cols.append(x[0].key)
        else:
            cols.append(x.key)
    return cols


def get_feature_key(feature):
    if type(feature) == _IndicatorColumn:
        return feature[0].key
    return feature.key


def prediction_from_df(file_path):
    df = pd.read_csv(file_path)
    data = df.as_matrix().tolist()
    columns = [{'title': v} for v in df.columns.values.tolist()]
    return {'data': data, 'columns': columns}


def get_summary(USER_ROOT, username, dataset_name):
    main_path = get_dataset_path(USER_ROOT, username, dataset_name)
    graph_json = os.path.join(main_path, SUMMARY)
    data = None
    if os.path.isfile(graph_json):
        with open(graph_json) as json_file:
            data = json.load(json_file)
    return data


def save_summary(USER_ROOT, username, dataset_name, data):
    main_path = get_dataset_path(USER_ROOT, username, dataset_name)
    graph_json = os.path.join(main_path, SUMMARY)
    with open(graph_json, 'w') as outfile:
        json.dump(data, outfile)


def get_tabular_graphs(USER_ROOT, username, dataset_name):
    main_path = get_dataset_path(USER_ROOT, username, dataset_name)
    graph_json = os.path.join(main_path, DATA_GRAPH)
    if os.path.isfile(graph_json):
        with open(graph_json) as json_file:
            data = json.load(json_file)
            return data
    return save_tabular_graphs(main_path, dataset_name, graph_json)


def save_tabular_graphs(main_path,dataset_name, graph_json):
    df = pd.read_csv(os.path.join(main_path, dataset_name + '.csv'))
    num_rows, df_as_json, norm, corr = get_norm_corr(df)
    data = {'data': json.loads(df_as_json), 'num_rows': num_rows, 'norm': norm, 'corr': corr}
    with open(graph_json, 'w') as outfile:
        json.dump(data, outfile)
        return data

def get_image_graphs(USER_ROOT, username, dataset_name):
    main_path = get_dataset_path(USER_ROOT, username, dataset_name)
    graph_json = os.path.join(main_path, DATA_GRAPH)
    if os.path.isfile(graph_json):
        with open(graph_json) as json_file:
            data = json.load(json_file)
            return data
    return None


def save_image_graphs(USER_ROOT, username, dataset_name, data):
    main_path = get_dataset_path(USER_ROOT, username, dataset_name)
    graph_json = os.path.join(main_path, DATA_GRAPH)
    with open(graph_json, 'w') as outfile:
        json.dump(data, outfile)
