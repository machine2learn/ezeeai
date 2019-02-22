import os
import itertools
from sklearn.model_selection import train_test_split
import pandas as pd
import csv


# TODO Perhaps to handle big files you can change this, to work with the filename instead
# TODO write test.
def split_train_test(percent, dataset_file, targets, dataframe):
    removed_ext = os.path.splitext(dataset_file)[0]
    train_file = "{}-train.csv".format(removed_ext)
    validation_file = "{}-validation.csv".format(removed_ext.replace('/train/', '/valid/'))
    percent = percent.split(',')
    percent = (int(percent[0]), int(percent[1]), int(percent[2]))
    if percent[2] == 0:
        test_size = percent[1] / 100
        if len(targets) == 1:
            target = targets[0]
            counts = dataframe[target].value_counts()
            if dataframe[target].dtype == 'object':
                dataframe = dataframe[dataframe[target].isin(counts[counts > 1].index)]
                target = dataframe[[target]]
                train_df, test_df = train_test_split(dataframe, test_size=test_size, stratify=target, random_state=42)
            else:
                train_df, test_df = train_test_split(dataframe, test_size=test_size, random_state=42)
        else:
            train_df, test_df = train_test_split(dataframe, test_size=test_size, random_state=42)
        train_df.to_csv(train_file, index=False)
        test_df.to_csv(validation_file, index=False)
        return train_file, validation_file, ""
    else:
        test_file = "{}-test.csv".format(removed_ext.replace('/train/', '/test/'))
        test_size = (100 - percent[0]) / 100
        if len(targets) == 1:
            target = targets[0]
            counts = dataframe[target].value_counts()
            if dataframe[target].dtype == 'object':
                dataframe = dataframe[dataframe[target].isin(counts[counts > 1].index)]
                target = dataframe[[target]]
                train_df, test_df = train_test_split(dataframe, test_size=test_size, stratify=target, random_state=42)
                test_len = int(round((percent[2] / 100) * len(test_df)))
                target = targets[0]
                target = test_df[[target]]
                val_df, test_df = train_test_split(test_df, test_size=test_len, stratify=target, random_state=42)
            else:
                train_df, test_df = train_test_split(dataframe, test_size=test_size, random_state=42)
                test_len = int(round((percent[2] / 100) * len(test_df)))
                val_df, test_df = train_test_split(test_df, test_size=test_len, random_state=42)
        else:
            train_df, test_df = train_test_split(dataframe, test_size=test_size, random_state=42)
            test_len = int(round((percent[2] / 100) * len(test_df)))
            val_df, test_df = train_test_split(test_df, test_size=test_len, random_state=42)

        train_df.to_csv(train_file, index=False)
        val_df.to_csv(validation_file, index=False)
        test_df.to_csv(test_file, index=False)
        return train_file, validation_file, test_file


def insert_data(df, categories, unique_values, default_list, frequent_values2frequency, SAMPLE_DATA_SIZE):
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


def clean_field_names(filename):
    args = {}
    if not has_header(filename):
        args['header'] = None
    df = pd.read_csv(filename, sep=None, engine='python', **args)
    df.columns = df.columns.astype(str)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')',
                                                                                                           '').str.replace(
        '.', '_')
    df.to_csv(filename, index=False)


def clean_field_names_df(file, filename):
    args = {}
    if not has_header(file, False):
        args['header'] = None
    df = pd.read_csv(file, sep=None, engine='python', **args)
    df.columns = df.columns.astype(str)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    df.to_csv(filename, index=False)
    return df


def check_train(train_file, targets):
    if len(targets) > 1:
        return True
    df = pd.read_csv(train_file)
    if df[targets[0]].dtype == 'object':
        if len(df[targets[0]].unique()) < 2:
            return False
    return True


def has_header(csvfile, close=True):
    if isinstance(csvfile, str):
        csvfile = open(csvfile, 'r')

    sniffer = csv.Sniffer()
    has_header = sniffer.has_header(csvfile.read(2048))
    if close:
        csvfile.close()
    else:
        csvfile.seek(0)
    return has_header
