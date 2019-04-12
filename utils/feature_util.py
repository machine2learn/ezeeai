import json
import os
import pandas as pd
from utils.sys_ops import get_dataset_path
from utils.visualize_util import get_norm_corr
from tensorflow.python.feature_column.feature_column import _IndicatorColumn

MAX_CATEGORICAL_SIZE = 2000
MAX_RANGE_SIZE = 100
MIN_RANGE_SIZE = 10


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


def get_tabular_graphs(APP_ROOT, username, dataset_name):
    main_path = get_dataset_path(APP_ROOT, username, dataset_name)
    graph_json = os.path.join(main_path, 'data_graphs.json')
    if os.path.isfile(graph_json):
        with open(graph_json) as json_file:
            data = json.load(json_file)
    else:
        df = pd.read_csv(os.path.join(main_path, dataset_name + '.csv'))
        num_rows, df_as_json, norm, corr = get_norm_corr(df)
        data = {'data': json.loads(df_as_json), 'num_rows': num_rows, 'norm': norm, 'corr': corr}
        with open(graph_json, 'w') as outfile:
            json.dump(data, outfile)
    return data


def get_image_graphs(APP_ROOT, username, dataset_name):
    main_path = get_dataset_path(APP_ROOT, username, dataset_name)
    graph_json = os.path.join(main_path, 'data_graphs.json')
    if os.path.isfile(graph_json):
        with open(graph_json) as json_file:
            data = json.load(json_file)
            return True, data
    else:
        return False, None

def save_image_graphs(APP_ROOT, username, dataset_name, data):
    main_path = get_dataset_path(APP_ROOT, username, dataset_name)
    graph_json = os.path.join(main_path, 'data_graphs.json')
    with open(graph_json, 'w') as outfile:
        json.dump(data, outfile)

# from collections import defaultdict
# from functools import reduce
#
# import numpy as np
#
# import dill as pkl
# import os


# def get_target_labels(targets, feature_types, fs):
#     if len(targets) > 1:
#         return None
#     target = targets[0]
#     target_type = feature_types[target]
#     # TODO labels if target type is a RANGE, BOOL, ...
#     if target_type == 'categorical' or target_type == 'hash':
#         return fs.cat_unique_values_dict[target]
#     elif 'range' in target_type:
#         return [str(a) for a in list(range(min(fs.df[target].values), max(fs.df[target].values)))]
#     return None

#
# def get_new_features(form, feat_defaults, targets, fs_list):
#     new_features = {}
#     for k, v in feat_defaults.items():
#         if k not in fs_list:
#             new_features[k] = form[k] if k not in targets else feat_defaults[k]
#     return new_features

#
# def get_default_features(feat_defaults, targets, fs_list, df):
#     new_features = {}
#     for k, v in feat_defaults.items():
#         if k not in fs_list and k not in targets:
#             new_features[k] = feat_defaults[k]
#     input_predict = {}
#     for k, v in new_features.items():
#         dtype = df[k].dtype
#         try:
#             if dtype == 'category':
#                 dtype = 'object'
#         except:
#             pass
#         input_predict[k] = np.array([v]).astype(dtype) if dtype == 'object' else np.array(
#             [float(v)]).astype(dtype)
#     # input_predict.pop(target, None)
#
#     return input_predict

#
# def save_scalers(df, targets, datatypes):
#     df = df.copy()
#     # df.drop(targets, axis=1, inplace=True)
#     scalers = {}
#     feature_types = group_by(df, datatypes)
#     for c in df.columns:
#         if c in targets:
#             continue
#         if feature_types[c] == "numerical":
#             mean = df[c].mean()
#             stdv = df[c].std()
#             norm_fn = lambda x: (x - mean) / stdv
#             scalers[c] = norm_fn
#     return scalers

#
# def normalize(df, path):
#     scalers = pkl.load(open(os.path.join(path, "scalers.pkl"), "rb"))
#     df = df.copy()
#     for c in scalers.keys():
#         df[c] = scalers[c](df[c])
#     return df

#
# def group_by(df, datatypes):
#     columns_types_dict = dict(zip(df.columns, datatypes))
#     v = {}
#     for col, datatype in columns_types_dict.items():
#         v[col] = datatype
#     return v
