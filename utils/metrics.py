import numpy as np
import os
import tensorflow as tf
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score, accuracy_score, r2_score
from scipy import interp
from sklearn.preprocessing import label_binarize


def store_predictions(has_targets, sess, final_pred, output):
    if has_targets:
        sess.set('y_true', output)
        sess.set('y_pred', np.array(final_pred['preds']))
        if 'logits' in final_pred:
            sess.set('logits', np.array(final_pred['logits']))


def roc_auc(y_test, y_score, classes):
    fpr = {}
    tpr = {}
    roc_auc = {}

    if len(classes) == 2:
        if np.max(y_score) > 1:
            y_score = sigmoid(y_score)
        fpr['bin'], tpr['bin'], _ = roc_curve(y_test.reshape(-1), y_score.reshape(-1), pos_label=classes[1])
        roc_auc['bin'] = auc(fpr['bin'], tpr['bin'])
        fpr['bin'] = fpr['bin'].tolist()
        tpr['bin'] = tpr['bin'].tolist()
        dict_results = {'roc_auc': roc_auc, 'fpr': fpr, 'tpr': tpr}

    else:
        if np.max(y_score) > 1:
            y_score = softmax(y_score, axis=1)

        y_test = label_binarize(y_test, classes=np.array(classes).astype(y_test.dtype))
        n_classes = y_test.shape[1]
        # y_score = y_score.reshape([-1, n_classes])

        for i in range(n_classes):
            fpr[classes[i]], tpr[classes[i]], _ = roc_curve(y_test[:, i], y_score[:, i])
            roc_auc[classes[i]] = auc(fpr[classes[i]], tpr[classes[i]])

        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        all_fpr = np.unique(np.concatenate([fpr[classes[i]] for i in range(n_classes)]))

        mean_tpr = np.zeros_like(all_fpr)
        for i in range(n_classes):
            mean_tpr += interp(all_fpr, fpr[classes[i]], tpr[classes[i]])

        # Finally average it and compute AUC
        mean_tpr /= n_classes

        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])
        dict_results = {'roc_auc': roc_auc, 'fpr': fpr, 'tpr': tpr}
        dict_results = to_list(dict_results)

    return dict_results


def precision_recall(y_test, y_score, classes):
    precision = {}
    recall = {}
    average_precision = {}

    if len(classes) == 2:
        if np.max(y_score) > 1:
            y_score = sigmoid(y_score)
        precision['bin'], recall['bin'], _ = precision_recall_curve(y_test.reshape(-1),
                                                                    y_score.reshape(-1), pos_label=classes[1])
        average_precision['bin'] = average_precision_score(y_test.reshape(-1),
                                                           y_score.reshape(-1), pos_label=classes[1])
        precision['bin'] = precision['bin'].tolist()
        recall['bin'] = recall['bin'].tolist()
        dict_results = {'precision': precision, 'recall': recall, 'average_precision': average_precision}
    else:
        if np.max(y_score) > 1:
            y_score = softmax(y_score, axis=1)
        y_test = label_binarize(y_test, classes=np.array(classes).astype(y_test.dtype))
        n_classes = y_test.shape[1]
        # y_score = y_score.reshape([-1, n_classes])
        precision = {}
        recall = {}
        average_precision = {}
        for i in range(n_classes):
            precision[classes[i]], recall[classes[i]], _ = precision_recall_curve(y_test[:, i],
                                                                                  y_score[:, i])
            average_precision[classes[i]] = average_precision_score(y_test[:, i], y_score[:, i])

        # Compute micro-average ROC curve and ROC area
        precision["micro"], recall["micro"], _ = precision_recall_curve(y_test.ravel(),
                                                                        y_score.ravel())
        average_precision["micro"] = average_precision_score(y_test, y_score,
                                                             average="micro")
        dict_results = {'precision': precision, 'recall': recall, 'average_precision': average_precision}
        dict_results = to_list(dict_results)
    return dict_results


def to_list(n_dict):
    out = {}
    for k, v in n_dict.items():
        out[k] = {}
        for k2, v2 in v.items():
            out[k][k2] = v2.tolist()
    return out


def softmax(X, theta=1.0, axis=None):
    # make X at least 2d
    y = np.atleast_2d(X)

    # find axis
    if axis is None:
        axis = next(j[0] for j in enumerate(y.shape) if j[1] > 1)

    # multiply y against the theta parameter,
    y = y * float(theta)

    # subtract the max for numerical stability
    y = y - np.expand_dims(np.max(y, axis=axis), axis)

    # exponentiate y
    y = np.exp(y)

    # take the sum along the specified axis
    ax_sum = np.expand_dims(np.sum(y, axis=axis), axis)

    # finally: divide elementwise
    p = y / ax_sum

    # flatten if X was 1D
    if len(X.shape) == 1: p = p.flatten()

    return p


def sigmoid(x, derivative=False):
    return x * (1 - x) if derivative else 1 / (1 + np.exp(-x))


def get_metrics(mode, y_true, y_pred, labels, target_len=1, logits=None):
    metrics = {}
    if mode == 'classification':
        roc = roc_auc(y_true, logits, labels)
        pr = precision_recall(y_true, logits, labels)
        metrics['roc'] = roc
        metrics['pr'] = pr
        metrics['accuracy'] = accuracy_score(y_true.reshape(-1), y_pred.reshape(-1).astype(y_true.dtype))
    else:
        if target_len > 1:

            y_pred = y_pred.reshape(-1, target_len)
            y_true = y_true.reshape(-1, target_len)
            metrics['y_true'] = y_true.tolist()
            metrics['y_pred'] = y_pred.tolist()

            y_valid = ~np.isnan(y_pred).any(axis=1)
            y_pred = y_pred[y_valid]
            y_true = y_true[y_valid]
            y_valid = ~np.isnan(y_true).any(axis=1)
            y_pred = y_pred[y_valid]
            y_true = y_true[y_valid]

            metrics['r2_score'] = r2_score(y_true, y_pred, multioutput='raw_values').tolist()
        else:

            y_pred = y_pred.reshape(-1)
            y_true = y_true.reshape(-1)
            metrics['y_true'] = y_true.tolist()
            metrics['y_pred'] = y_pred.tolist()

            y_valid = ~np.isnan(y_pred)
            y_pred = y_pred[y_valid]
            y_true = y_true[y_valid]
            y_valid = ~np.isnan(y_true)
            y_pred = y_pred[y_valid]
            y_true = y_true[y_valid]
            metrics['r2_score'] = r2_score(y_true, y_pred)

    return metrics


def train_eval_graphs(path):
    train = {'title': '', 'loss': []}
    eval = {'title': '', 'loss': []}

    train_events = [os.path.join(path, f) for f in os.listdir(path) if f.startswith('events.out.tfevents')]
    eval_events = [os.path.join(path, 'eval', f) for f in os.listdir(os.path.join(path, 'eval')) if
                   f.startswith('events.out.tfevents')]

    train_events.sort(key=lambda x: os.path.getmtime(x))
    eval_events.sort(key=lambda x: os.path.getmtime(x))

    train_summary = train_events[0]
    eval_summary = eval_events[0]

    for e in tf.train.summary_iterator(train_summary):
        for v in e.summary.value:
            metric = v.tag.split('_1')[0]
            if metric in ['accuracy', 'r_squared', 'loss']:
                if metric not in train:
                    train[metric] = []
                train[metric].append(v.simple_value)

    for e in tf.train.summary_iterator(eval_summary):
        for v in e.summary.value:
            metric = v.tag.split('_1')[0]
            if metric in ['accuracy', 'r_squared', 'loss']:
                if metric not in eval:
                    eval[metric] = []
                eval[metric].append(v.simple_value)

    return train, eval



