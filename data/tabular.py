from functools import reduce

from sklearn.model_selection import train_test_split
from tensorflow.python.feature_column.feature_column import _IndicatorColumn

from data.dataset import make_csv_dataset
from data.feature_selection import FeatureSelection
from utils import args

import pandas as pd
import itertools
import os
import tensorflow as tf
import numpy as np
from utils.feature_util import get_feature_key, get_feature_names

SAMPLE_DATA_SIZE = 5


class Tabular:
    def __init__(self, name, file):
        self._name = None
        self._file = None

        self._train_file = None
        self._validation_file = None
        self._test_file = None

        self._df = None

        self._normalize = False

        self._fs = None
        self._defaults = None
        self._converted_defaults = None
        self._keyed_defaults = None
        self._categories = None  # session -> category_list
        self._column_categories = None
        self._summary = None  # session -> data
        self._targets = None

        self._all_feature_columns = None  # session -> all_features
        self._feature_columns = None  # session -> features
        self._feature_names = None

        self._train_size = None
        self._split = None

        self.set_file(file)
        self.set_name(name)
        self.load_features()
        self._base_path = self._file.replace(self._name + '.csv', '')

    def set_name(self, name):
        args.assert_type(str, name)
        self._name = name

    def get_name(self):
        return self._name

    def set_file(self, file):
        args.assert_file(file)
        self._file = file

    def get_file(self):
        return self._file

    def set_base_path(self, path):
        args.assert_folder(path)
        self._base_path = path

    def get_base_path(self):
        return self._base_path

    def set_train_file(self, file):
        args.assert_file(file)
        self._train_file = file

    def get_train_file(self):
        return self._train_file

    def set_validation_file(self, file):
        args.assert_file(file)
        self._validation_file = file

    def get_validation_file(self):
        return self._validation_file

    def set_test_file(self, file):
        # args.assert_file(file)
        args.assert_type((str, list), file)
        self._test_file = file

    def get_test_file(self):
        return self._test_file

    def get_df(self):
        return self._df

    def set_df(self, df):
        args.assert_type(pd.DataFrame, df)
        self._df = df

    def get_normalize(self):
        return self._normalize

    def set_normalize(self, norm):
        args.assert_type(bool, norm)
        self._normalize = norm

    def get_feature_selection(self):
        return self._fs

    def set_feature_selection(self, fs):
        args.assert_type(FeatureSelection, fs)
        self._fs = fs

    def get_defaults(self):
        return self._defaults

    def get_converted_defaults(self):
        return self._converted_defaults

    def get_keyed_defaults(self):
        return self._keyed_defaults

    def set_defaults(self, defaults):
        args.assert_type(dict, defaults)
        self._defaults = defaults
        self.update_converted_defaults()

    def get_categories(self):
        return self._categories

    def set_categories(self, categories):
        args.assert_type(list, categories)
        self._categories = categories

    def get_column_categories(self):
        return self._column_categories

    def set_column_categories(self, categories):
        args.assert_type(dict, categories)
        self._column_categories = categories

    def get_data_summary(self):
        return self._summary

    def set_data_sumary(self, ds):
        args.assert_type(pd.DataFrame, ds)
        self._summary = ds

    def get_targets(self):
        return self._targets

    def set_targets(self, targets):
        args.assert_type(list, targets)
        self._targets = targets

    def get_feature_columns(self):
        return self._feature_columns

    def get_feature_names(self):
        return self._feature_names

    def set_feature_columns(self, fc):
        args.assert_type(list, fc)
        self._feature_columns = fc
        self._feature_names = get_feature_names(self.get_feature_columns())

    def get_all_feature_columns(self):
        return self._all_feature_columns

    def set_all_feature_columns(self, fc):
        args.assert_type(list, fc)
        self._all_feature_columns = fc

    def set_train_size(self):
        if self._train_file is not None:
            self._train_size = len(pd.read_csv(self._train_file))

    def get_train_size(self):
        if self._train_file is not None:
            if self._train_size is None:
                self.set_train_size()
            return self._train_size
        return None

    def get_split(self):
        return self._split

    def set_split(self, split):
        args.assert_type(str, split)
        self._split = split

    def _assign_category(self):
        fs = FeatureSelection(self.get_df())
        self.set_feature_selection(fs)
        category_list, unique_values, default_list, frequent_values2frequency = fs.assign_category(self.get_df())
        return category_list, unique_values, default_list, frequent_values2frequency

    def _insert_data_summary(self, unique_values, default_list, frequent_values2frequency,
                             SAMPLE_DATA_SIZE):
        df = self.get_df()
        categories = self.get_categories()
        df = df.dropna(axis=0)
        data = df.head(SAMPLE_DATA_SIZE).T
        data.insert(0, 'Defaults', default_list.values())
        data.insert(0, '(most frequent, frequency)', frequent_values2frequency.values())
        data.insert(0, 'Unique Values', unique_values)
        data.insert(0, 'Category', categories)
        sample_column_names = ["Sample {}".format(i) for i in range(1, SAMPLE_DATA_SIZE + 1)]
        data.columns = list(
            itertools.chain(['Category', '#Unique Values', '(Most frequent, Frequency)', 'Defaults'],
                            sample_column_names))
        return data

    def get_new_features(self, form):
        fs_list = self.get_feature_selection().group_by(self.get_categories())['none']
        new_features = {}
        for k, v in self.get_defaults().items():
            if k not in fs_list:
                new_features[k] = form[k] if k not in self.get_targets() else self.get_defaults()[k]
        return new_features

    def load_features(self):
        self.set_df(pd.read_csv(self.get_file()))
        df = self.get_df()
        df.reset_index(inplace=True, drop=True)
        categories, unique_values, default_list, frequent_values2frequency = self._assign_category()
        self.set_categories(categories)

        self.set_data_sumary(self._insert_data_summary(unique_values, default_list, frequent_values2frequency,
                                                       SAMPLE_DATA_SIZE))
        default_values = [str(v) for v in default_list.values()]
        self.set_defaults(dict(zip(self.get_data_summary().index.tolist(), default_values)))

    def update_targets(self, targets):
        fs = self.get_feature_selection()
        categories = self.get_categories()
        summary_data = self.get_data_summary()
        df = self.get_df()

        if len(targets) > 1:
            for t in targets:
                if summary_data.Category[t] != 'numerical':
                    return False

        self.set_targets(targets)
        if len(targets) == 1:
            target_type = summary_data.Category[targets[0]]
            if target_type == 'range':
                new_categ_list = []
                for categ, feature in zip(categories, df.columns):
                    new_categ_list.append(categ if feature != targets[0] else 'categorical')
                self.set_categories(new_categ_list)
                summary_data.Category = new_categ_list
                fs.update(categories, dict(zip(summary_data.index.tolist(), summary_data.Defaults)))

        return True

    def update_feature_columns(self):
        categories = self.get_categories()
        fs = self.get_feature_selection()
        training_path = self.get_train_file()
        targets = self.get_targets()
        self.set_feature_columns(fs.create_tf_features(categories, targets, self.get_normalize(), training_path))
        self.set_all_feature_columns(fs.create_tf_features(categories, targets, self.get_normalize(), training_path,
                                                           without_label=False))

    def update_features(self, cat_columns, default_values):
        old_categories = self.get_categories()
        self.set_categories(cat_columns)
        for i in range(len(cat_columns)):
            if 'none' in cat_columns[i]:
                cat_columns[i] = 'none'
        summary_data = self.get_data_summary()
        summary_data.Category = cat_columns
        default_values = [str(v) for v in default_values]
        summary_data.Defaults = default_values
        self.set_defaults(dict(zip(summary_data.index.tolist(), default_values)))
        self.get_feature_selection().update(cat_columns, dict(zip(summary_data.index.tolist(), default_values)))

        column_categories = {}
        for label, old_cat in zip(summary_data.index, old_categories):
            new_cat = summary_data.Category[label]  # if data.Category[label] != 'range' else 'int-range'
            cat = new_cat + '-' + old_cat.replace('none-', '') if 'none' in new_cat else new_cat
            # writer.add_item('COLUMN_CATEGORIES', label, cat)
            column_categories[label] = cat
        self.set_column_categories(column_categories)

    def split_dataset(self, percent=None):
        percent = percent or self.get_split()
        self.set_split(percent)
        file = self.get_file()
        basename = os.path.basename(file)

        train_file = file.replace(basename, f'train/{basename}')
        validation_file = file.replace(basename, f'valid/{basename}')

        percent = percent.split(',')
        percent = (int(percent[0]), int(percent[1]), int(percent[2]))
        targets = self.get_targets()

        df = self.get_df()
        stratify = None
        val_frac = percent[1] / 100

        if len(targets) == 1 and self.get_df()[targets[0]].dtype == 'object':
            counts = df[targets[0]].value_counts()
            df = df[df[targets[0]].isin(counts[counts > 1].index)]
            stratify = df[[targets[0]]]

        train_df, val_df = train_test_split(df, test_size=val_frac, stratify=stratify, random_state=42)

        if percent[2] != 0:
            test_file = file.replace(basename, f'test/{basename}')
            test_size = int(round((percent[2] / 100) * len(df)))
            if len(targets) == 1 and self.get_df()[targets[0]].dtype == 'object':
                counts = train_df[targets[0]].value_counts()
                train_df = train_df[train_df[targets[0]].isin(counts[counts > 1].index)]
                stratify = train_df[[targets[0]]]
            train_df, test_df = train_test_split(train_df, test_size=test_size, stratify=stratify, random_state=42)
            test_df.to_csv(test_file, index=False)
            self.set_test_file(test_file)

        train_df.to_csv(train_file, index=False)
        val_df.to_csv(validation_file, index=False)

        self.set_train_file(train_file)
        self.set_validation_file(validation_file)

    def get_params(self):
        return {'split': self.get_split(), 'targets': self.get_targets(), 'category_list': self.get_column_categories(),
                'normalize': self.get_normalize()}

    def get_num_outputs(self):
        targets = self.get_targets()
        df = self.get_df()
        if len(targets) > 1:
            return len(targets)

        if df[targets[0]].dtype == "object":
            if len(df[targets[0]].unique()) <= 2:
                return 1
            return len(df[targets[0]].unique())
        return 1

    def get_num_inputs(self):
        fs_list = self.get_feature_selection().group_by(self.get_categories())['none']
        filtered = [f for f in self.get_feature_columns() if get_feature_key(f) not in fs_list]
        # filter feature_columns
        shapes = [x._variable_shape.num_elements() for x in filtered]
        return reduce(lambda x, y: x + y, shapes)

    def get_target_labels(self):
        if len(self.get_targets()) > 1:
            return None
        target = self.get_targets()[0]
        target_type = self.get_data_summary().Category[target]
        fs = self.get_feature_selection()
        if target_type == 'categorical' or target_type == 'hash':
            return fs.cat_unique_values_dict[target]
        elif 'range' in target_type:
            return [str(a) for a in list(range(min(fs.df[target].values), max(fs.df[target].values)))]
        return None

    def get_dtypes(self):
        return self.get_feature_selection().group_by(self.get_categories())

    def get_mode(self):
        if self.get_data_summary().Category[self.get_targets()[0]] == 'numerical':
            return 'regression'
        return 'classification'

    def update_converted_defaults(self):
        dtypes = self.get_dtypes()
        defaults = self.get_defaults().copy()
        defaults.update({key: float(defaults[key]) for key in dtypes['numerical']})
        if 'range' in dtypes:
            defaults.update({key: int(float(defaults[key])) for key in dtypes['range']})

        self._converted_defaults = [[key] for key in defaults.values()]
        self._keyed_defaults = defaults

    def to_array(self, features):
        df = self.get_df()[self.get_feature_names()]
        feature_types = self.get_dtypes()
        for c in df.columns:
            if c in features.keys():
                if df[c].dtype == 'object':
                    if feature_types[c] == 'hash':
                        try:
                            features[c] = int(float(features[c]))
                        except:
                            pass
                    df[c] = df[c].astype('category')
                    mapp = {y: x for x, y in dict(enumerate(df[c].cat.categories)).items()}
                    features[c] = float(mapp[features[c]])
                else:
                    features[c] = float(features[c])
        feats = df[self.get_feature_names()].append(
            pd.DataFrame(pd.Series(features)).transpose()[self.get_feature_names()]).tail(1)
        input_predict = feats.values.reshape(-1)
        return input_predict

    def from_array(self, features):
        df = self.get_df()[self.get_feature_names()]
        feature_types = self.get_dtypes()
        for c in df.columns:
            if c in features.keys():
                if df[c].dtype == 'object':
                    df[c] = df[c].astype('category')
                    mapp = {x: y for x, y in dict(enumerate(df[c].cat.categories)).items()}
                    features[c] = np.vectorize(mapp.get)(features[c])
                    if feature_types[c] == 'hash':
                        features[c] = features[c].astype(str)
                else:
                    features[c] = features[c].astype(df[c].dtype)
        return features

    def create_feat_array(self, features):
        for t in self.get_targets():
            del features[t]
        features = {k: features[k] for k in self.get_feature_names()}
        return self.to_array(features)

    def clean_values(self, df):
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        for c in df.columns.values:
            df[c] = df[c].fillna(self._keyed_defaults[c])
            df[c] = df[c].astype(type(self._keyed_defaults[c]))
        return df

    def make_numpy_array(self, file, sel_target=None):
        df = self.clean_values(pd.read_csv(file))

        target = sel_target or self.get_targets()[0]

        y = df[target].values
        df.drop(self.get_targets(), axis=1, inplace=True)

        df = df[self.get_feature_names()]
        for c in df.columns:
            if df[c].dtype == 'object':
                df[c] = df[c].astype('category')
        cat_columns = df.select_dtypes(['category']).columns
        df[cat_columns] = df[cat_columns].apply(lambda x: x.cat.codes)

        return df.values, y

    def get_categorical_features(self):
        categorical_features = []
        df = self.get_df()[self.get_feature_names()]
        for c in df.columns:
            if df[c].dtype == "object":
                categorical_features.append(c)
            else:
                for x in self.get_feature_columns():
                    if type(x) == _IndicatorColumn and x[0].key == c:
                            categorical_features.append(c)

        categorical_index = [list(df.columns.values).index(x) for x in categorical_features]
        categorical_names = {k: df[k].unique() for k in categorical_features}
        return categorical_features, categorical_index, categorical_names

    def train_input_fn(self, batch_size, num_epochs):
        csv_dataset = make_csv_dataset([self.get_train_file()], batch_size=batch_size, shuffle=True,
                                       label_names=self.get_targets(), num_epochs=num_epochs,
                                       column_defaults=self.get_converted_defaults())
        return csv_dataset

    def validation_input_fn(self, batch_size):
        csv_dataset = make_csv_dataset([self.get_validation_file()], batch_size=batch_size, shuffle=False,
                                       label_names=self.get_targets(), num_epochs=1,
                                       column_defaults=self.get_converted_defaults())
        return csv_dataset

    def test_input_fn(self, batch_size, file=None):
        file = file or self.get_test_file()[0] if isinstance( self.get_test_file(), list) else  self.get_test_file()  #TODO
        csv_dataset = make_csv_dataset([file], batch_size=batch_size, shuffle=False,
                                       label_names=self.get_targets(), num_epochs=1,
                                       column_defaults=self.get_converted_defaults())
        return csv_dataset

    def input_predict_fn(self, features):
        df = self.get_df()
        for t in self.get_targets():
            del features[t]
        features = {k: features[k] for k in get_feature_names(self.get_feature_columns())}
        for k, v in features.items():
            features[k] = np.array([v]).astype(df[k].dtype) if df[k].dtype == 'object' else np.array(
                [float(v)]).astype(df[k].dtype)
        return tf.estimator.inputs.numpy_input_fn(x=features, y=None, num_epochs=1, shuffle=False)

    def serving_input_receiver_fn(self):
        feature_spec = tf.feature_column.make_parse_example_spec(self.get_feature_columns())
        receiver_tensors = {k: tf.placeholder(v.dtype, [None, 1]) for k, v in feature_spec.items()}
        return tf.estimator.export.ServingInputReceiver(receiver_tensors=receiver_tensors,
                                                        features=receiver_tensors)
