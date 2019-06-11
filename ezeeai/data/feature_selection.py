import itertools
import tensorflow as tf
import pandas as pd

from collections import defaultdict


class FeatureSelection:

    def __init__(self, df, max_categorical_size, max_range_size, min_range_size):
        self.MAX_CATEGORICAL_SIZE = max_categorical_size
        self.MAX_RANGE_SIZE = max_range_size
        self.MIN_RANGE_SIZE = min_range_size
        self.features = {}
        self.df = df
        self.numerical_columns = self.select_columns_with_type('floating')

        self.int_columns = self.select_columns_with_type('integer')
        self.unique_value_size_dict = {key: self.df[key].unique().shape[0] for key in self.int_columns}

        self.bool_columns = self.select_columns_with_type('bool')
        self.unique_value_size_dict.update(dict(itertools.product(self.bool_columns, [2])))

        self.cat_or_hash_columns = self.select_columns_with_type('flexible', 'object')
        self.populate_hash_and_categorical()

        self.column_list = {'numerical': self.numerical_columns,
                            'bool': self.bool_columns,
                            'categorical': self.categorical_columns,
                            'int-range': [key for key in self.int_columns if
                                          self.unique_value_size_dict[key] < self.MAX_RANGE_SIZE],
                            'int-hash': [key for key in self.int_columns if
                                         self.unique_value_size_dict[key] >= self.MAX_RANGE_SIZE],
                            'hash': self.hash_columns}
        self.populate_defaults()

    def populate_defaults(self):
        self.medians = self.df.median().to_dict()
        self.modes = self.df.mode().iloc[0, :].to_dict()
        self.frequent_values2frequency = {}
        for col in self.df.columns:
            val2freq = self.df[col].value_counts().head(1).to_dict()
            self.frequent_values2frequency.update({col: (next(iter(val2freq.items())))})

        self.defaults = self.modes
        for col in self.numerical_columns:
            self.defaults[col] = self.medians[col]

    def feature_dict(self):
        return dict(itertools.chain.from_iterable(
            [itertools.product(self.column_list[key], [key]) for key in self.column_list]))

    def populate_hash_and_categorical(self):
        self.cat_unique_values_dict = {}
        self.categorical_columns = []
        self.hash_columns = []

        for col in self.cat_or_hash_columns:
            unique = self.df[col].unique().tolist()
            if (len(unique) < self.MAX_CATEGORICAL_SIZE):
                self.cat_unique_values_dict[col] = unique
                self.categorical_columns.append(col)
            else:
                self.hash_columns.append(col)
            self.unique_value_size_dict[col] = len(unique)

        for col in self.int_columns[:]:
            unique = self.unique_value_size_dict[col]
            if (unique < self.MIN_RANGE_SIZE):
                self.cat_unique_values_dict[col] = self.df[col].unique().tolist()
                self.categorical_columns.append(col)
                self.int_columns.remove(col)

    def group_by(self, datatypes):
        columns_types_dict = dict(zip(self.df.columns, datatypes))
        v = defaultdict(list)
        for col, datatype in columns_types_dict.items():
            v[datatype].append(col)
        return v

    def remove_label(self, datatypes, targets):
        for _, v in datatypes.items():
            for target in targets:
                if target in v:
                    v.remove(target)

    def create_tf_features(self, datatypes, targets, normalize, training_path, without_label=True):

        feature_types = self.group_by(datatypes)
        if without_label:
            self.remove_label(feature_types, targets)

        df = pd.read_csv(training_path)
        numerical_features = []

        for key in feature_types['numerical']:
            norm_fn = None
            if normalize and df[key].nunique() > 1:
                mean = df[key].mean()
                stdv = df[key].std()
                norm_fn = lambda x: (x - mean) / stdv
            numerical_features.append(tf.feature_column.numeric_column(key, normalizer_fn=norm_fn))

        range_features = [tf.feature_column.indicator_column(
            tf.feature_column.categorical_column_with_identity(key, self.df[key].max() + 1)) for key in
            feature_types['range']]

        categorical_features = []
        for feature in feature_types['categorical']:
            if feature in self.bool_columns:
                vocab_list = ['True', 'False']
            else:
                vocab_list = self.stringify(
                    self.cat_unique_values_dict.get(feature, self.df[feature].unique().tolist()))
            categorical_features.append(tf.feature_column.indicator_column(
                tf.feature_column.categorical_column_with_vocabulary_list(feature, vocab_list)))

        hash_features = [tf.feature_column.indicator_column(
            tf.feature_column.categorical_column_with_hash_bucket(key, 2 * self.unique_value_size_dict[key])) for key in
            feature_types['hash']]

        self.feature_columns = list(itertools.chain.from_iterable(
            [numerical_features, categorical_features, hash_features, range_features]))

        return self.feature_columns

    def select_columns_with_type(self, *dftype):
        return self.df.select_dtypes(include=dftype).columns.tolist()

    def stringify(self, list_param):
        return [str(k) for k in list_param]

    def update(self, categories, defaults):
        for i, c in enumerate(self.df.columns):
            if categories[i] == 'categorical' or categories[i] == 'hash':
                self.df[c] = self.df[c].astype('object')
                if categories[i] == 'categorical':
                    self.df[c] = self.df[c].values.astype('str')
        self.numerical_columns = self.select_columns_with_type('floating')

        self.int_columns = self.select_columns_with_type('integer')
        self.unique_value_size_dict = {key: self.df[key].unique().shape[0] for key in self.int_columns}

        self.bool_columns = self.select_columns_with_type('bool')
        self.unique_value_size_dict.update(dict(itertools.product(self.bool_columns, [2])))

        self.cat_or_hash_columns = self.select_columns_with_type('flexible', 'object')
        self.populate_hash_and_categorical()

        self.column_list = {'numerical': self.numerical_columns,
                            'bool': self.bool_columns,
                            'categorical': self.categorical_columns,
                            'int-range': [key for key in self.int_columns if
                                          self.unique_value_size_dict[key] < self.MAX_RANGE_SIZE],
                            'int-hash': [key for key in self.int_columns if
                                         self.unique_value_size_dict[key] >= self.MAX_RANGE_SIZE],
                            'hash': self.hash_columns}

        self.defaults = defaults

    def assign_category(self, df):
        feature_dict = self.feature_dict()
        unique_values = [self.unique_value_size_dict.get(key, -1) for key in df.columns]
        category_list = [feature_dict[key] for key in df.columns]
        default_list = self.defaults
        frequent_values2frequency = self.frequent_values2frequency
        return category_list, unique_values, default_list, frequent_values2frequency
