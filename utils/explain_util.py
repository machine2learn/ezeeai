import numpy as np
import pandas as pd
from scipy import stats


MAX_FEATURES = 10


# def explain_return(sess, new_features, result, targets):
#     if result is None:
#         return 'Model\'s structure does not match the new parameter configuration'
#     if isinstance(sess.get_helper(), Image):
#
#         pass
#     else:
#         sess.set("new_features", {k: new_features[k] for k in new_features.keys() if k not in targets})
#         if result.mode == 'regression':
#             graphs, predict_table = get_reg_explain(result)
#             sess.set('type', 'regression')
#         else:
#             graphs, predict_table = get_class_explain(result)
#             sess.set('type', 'class')
#         sess.set('dict_graphs', graphs)
#         sess.set('dict_table', predict_table)
#         return 'ok'
#


def create_graphs(k, dict_list):
    graphs = {}
    graphs[k] = {}
    graphs[k]['labels'] = []
    graphs[k]['data'] = []
    for a in dict_list:
        graphs[k]['labels'].append(a[0])
        graphs[k]['data'].append(float("{0:.3f}".format(a[1])))
    return graphs


def get_class_explain(result):
    predict_table = {}
    graphs = {}
    for i in range(0, len(result.top_labels)):
        k = 'NOT ' + result.class_names[result.top_labels[i]] + ' |  ' + result.class_names[result.top_labels[i]]
        graphs[k] = {}
        graphs[k]['labels'] = []
        graphs[k]['data'] = []
        for a in result.as_list(label=result.top_labels[i]):
            graphs[k]['labels'].append(a[0])
            graphs[k]['data'].append(float("{0:.3f}".format(a[1])))
    predict_table['columns'] = []
    predict_table['data'] = []
    for c, d in zip(result.class_names, result.predict_proba):
        predict_table['columns'].append(c)
        predict_table['data'].append(float("{0:.3f}".format(d)))
    predict_table = clean_predict_table(predict_table)
    return graphs, predict_table


def get_reg_explain(result):
    predict_table = {}
    graphs = create_graphs('negative/positive', result.as_list())
    predict_table['max_value'] = float("{0:.3f}".format(result.max_value))
    predict_table['min_value'] = float("{0:.3f}".format(result.min_value))
    predict_table['predicted_value'] = float("{0:.3f}".format(result.predicted_value))
    return graphs, predict_table


def clean_predict_table(predict_table):
    new_predict_table = predict_table
    array_data = np.array(predict_table['data'])
    if len(predict_table['columns']) > MAX_FEATURES:
        new_predict_table = {'columns': [], 'data': []}
        ind = np.argpartition(array_data, -MAX_FEATURES)[-MAX_FEATURES:]
        for i in range(0, len(predict_table['columns'])):
            if i in ind:
                new_predict_table['columns'].append(predict_table['columns'][i])
                new_predict_table['data'].append(predict_table['data'][i])

        new_predict_table['columns'].append('others')
        new_predict_table['data'].append(1 - np.sum(np.array(new_predict_table['data'])))
    return new_predict_table


def check_input(num_feat, top_labels, max_feat, max_labels):
    if not num_feat \
            or int(num_feat) < 1 \
            or int(num_feat) > max_feat:
        return 'Wrong number of features. Please try again.'

    if not top_labels \
            or int(top_labels) < 1 \
            or int(top_labels) > max_labels:
        return 'Wrong number of labels. Please try again.'

    return None


def generate_ice_df(request, df, file, targets, dtypes):

    feature_selected = request.get_json()['explain_feature']
    feature_values = request.get_json()['features_values'].copy()
    for t in targets:
        feature_values[t] = None

    # TODO type categorical/ float / ...
    if feature_selected in dtypes['numerical']:
        mu, sig = stats.norm.fit(df[feature_selected].values)
        min = -2 * sig
        max = 2 * sig
        posible_values = np.linspace(min, max, num= 40).tolist()
        # posible_values = df[feature_selected].unique()
        # posible_values = [float(x) for x in posible_values]
        # posible_values.sort()

    else:
        posible_values = df[feature_selected].unique()
        posible_values.sort()
        posible_values = [str(x) for x in posible_values]


    row_n = len(posible_values)

    features = pd.DataFrame(pd.Series(feature_values)).transpose()
    new_df = pd.concat([features] * row_n, ignore_index=True)
    new_df[feature_selected] = posible_values

    # columns = list(df.columns)
    # new_df = new_df[columns]  # Reorder

    file_path = file.split('.csv')[0] + '_ice_explain.csv'
    new_df.to_csv(file_path, index=False)

    return file_path, posible_values


def get_exp_target_prediction(targets, exp_target, final_pred, dtypes):
    index = targets.index(exp_target) if len(targets) > 1 else None  # Target index in targets
    # TODO
    if index is not None:
        if exp_target in dtypes['numerical']:
            return [float(x[index]) for x in final_pred['preds']] , None
        return final_pred['preds'][index], [[float(score) for score in scores[index]] for scores in final_pred['scores']]

    if exp_target in dtypes['numerical']:
        return [float(x) for x in final_pred['preds']], None
    return final_pred['preds'], [[float(score) for score in scores] for scores in final_pred['scores']]
