from collections import defaultdict
from functools import reduce

import numpy as np
import pandas as pd
import dill as pkl
import os

from tensorflow.python.feature_column.feature_column import _IndicatorColumn

MAX_CATEGORICAL_SIZE = 2000
MAX_RANGE_SIZE = 100
MIN_RANGE_SIZE = 10


def reorder_request(features, categories, defaults, list_features):
    dict_features = {}
    for f, c, d in zip(features, categories, defaults):
        dict_features[f] = {}
        dict_features[f]['category'] = c
        dict_features[f]['default'] = d
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


def get_target_labels(targets, feature_types, fs):
    if len(targets) > 1:
        return None
    target = targets[0]
    target_type = feature_types[target]
    # TODO labels if target type is a RANGE, BOOL, ...
    if target_type == 'categorical' or target_type == 'hash':
        return fs.cat_unique_values_dict[target]
    elif 'range' in target_type:
        return [str(a) for a in list(range(min(fs.df[target].values), max(fs.df[target].values)))]
    return None


def write_features(old_categories, data):
    column_categories = {}
    for label, old_cat in zip(data.index, old_categories):
        new_cat = data.Category[label]  # if data.Category[label] != 'range' else 'int-range'
        cat = new_cat + '-' + old_cat.replace('none-', '') if 'none' in new_cat else new_cat
        # writer.add_item('COLUMN_CATEGORIES', label, cat)
        column_categories[label] = cat
    # writer.write_config(config_file)
    return column_categories

#
#
# def write_features(old_categories, data, writer, config_file):
#     for label, old_cat in zip(data.index, old_categories):
#         new_cat = data.Category[label]  # if data.Category[label] != 'range' else 'int-range'
#         cat = new_cat + '-' + old_cat.replace('none-', '') if 'none' in new_cat else new_cat
#         writer.add_item('COLUMN_CATEGORIES', label, cat)
#     writer.write_config(config_file)
#

def get_new_features(form, feat_defaults, targets, fs_list):
    new_features = {}
    for k, v in feat_defaults.items():
        if k not in fs_list:
            new_features[k] = form[k] if k not in targets else feat_defaults[k]
    return new_features


def get_default_features(feat_defaults, targets, fs_list, df):
    new_features = {}
    for k, v in feat_defaults.items():
        if k not in fs_list and k not in targets:
            new_features[k] = feat_defaults[k]
    input_predict = {}
    for k, v in new_features.items():
        dtype = df[k].dtype
        try:
            if dtype == 'category':
                dtype = 'object'
        except:
            pass
        input_predict[k] = np.array([v]).astype(dtype) if dtype == 'object' else np.array(
            [float(v)]).astype(dtype)
    # input_predict.pop(target, None)

    return input_predict


def check_targets(feature_types, targets):
    if len(targets) > 1:
        for t in targets:
            if feature_types[t] != 'numerical':
                return False
    return True


def calc_num_outputs(df, targets):
    if len(targets) > 1:
        return len(targets)
    else:
        if df[targets[0]].dtype == "object":
            if len(df[targets[0]].unique()) <= 2:
                return 1
            else:
                return len(df[targets[0]].unique())
        else:
            return 1


def get_categorical_features(df, feature_columns):
    categorical_features = []
    for c in df.columns:
        if df[c].dtype == "object":
            categorical_features.append(c)
        else:
            for x in feature_columns:
                if type(x) == _IndicatorColumn:
                    if x[0].key == c:
                        categorical_features.append(c)
    return categorical_features


def to_one_hot(df, feature_columns):
    df = df.copy()
    for c in df.columns:
        is_categorical = False
        for x in feature_columns:
            if type(x) == _IndicatorColumn:
                if x[0].key == c:
                    is_categorical = True
        unique = len(df[c].unique())
        if df[c].dtype == "object" or is_categorical or (
                df[c].dtype in [np.dtype('int64'), np.dtype('int32')] and unique < MAX_RANGE_SIZE):
            if unique <= 2 or unique > MAX_CATEGORICAL_SIZE:
                df[c] = df[c].astype('category')
                mapp = {y: x for x, y in dict(enumerate(df[c].cat.categories)).items()}
                df[c] = df[c].map(mapp)
            else:
                oh = pd.get_dummies(df[c])
                names = {v: c + "_" + str(v) for v in oh.columns.values}
                oh = oh.rename(names, axis="columns")
                df[oh.columns.values] = oh
                del df[c]
    return df


def get_label_names(df, targets, fc):
    is_categorical = False
    for x in fc:
        if type(x) == _IndicatorColumn:
            if x[0].key == targets[0]:
                is_categorical = True
    if len(targets) == 1:
        unique = len(df[targets[0]].unique())
        c = targets[0]
        if df[c].dtype == "object" or is_categorical or (
                df[c].dtype in [np.dtype('int64'), np.dtype('int32')] and unique < MAX_RANGE_SIZE):
            if unique > 2 and unique < MAX_CATEGORICAL_SIZE:
                oh = pd.get_dummies(df[targets[0]])
                names = {v: targets[0] + "_" + str(v) for v in oh.columns.values}
                oh = oh.rename(names, axis="columns")
                return oh.columns
    return targets


def save_scalers(df, targets, datatypes):
    df = df.copy()
    # df.drop(targets, axis=1, inplace=True)
    scalers = {}
    feature_types = group_by(df, datatypes)
    for c in df.columns:
        if c in targets:
            continue
        if feature_types[c] == "numerical":
            mean = df[c].mean()
            stdv = df[c].std()
            norm_fn = lambda x: (x - mean) / stdv
            scalers[c] = norm_fn
    return scalers


def normalize(df, path):
    scalers = pkl.load(open(os.path.join(path, "scalers.pkl"), "rb"))
    df = df.copy()
    for c in scalers.keys():
        df[c] = scalers[c](df[c])
    return df


def group_by(df, datatypes):
    columns_types_dict = dict(zip(df.columns, datatypes))
    v = {}
    for col, datatype in columns_types_dict.items():
        v[col] = datatype
    return v


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


def calc_num_inputs(feature_columns, fs_list):
    filtered = [f for f in feature_columns if get_feature_key(f) not in fs_list]
    # filter feature_columns
    shapes = [x._variable_shape.num_elements() for x in filtered]
    return reduce(lambda x, y: x + y, shapes)
