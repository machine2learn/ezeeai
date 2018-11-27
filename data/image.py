import tensorflow as tf
import os
import pandas as pd


class Image:
    def __init__(self, name, file):
        pass
        # self._name = None
        # self._file = None
        #
        # self._train_file = None
        # self._validation_file = None
        # self._test_file = None
        #
        # self._df = None
        #
        # self._normalize = False
        #
        # self._fs = None
        # self._defaults = None
        # self._converted_defaults = None
        # self._keyed_defaults = None
        # self._categories = None  # session -> category_list
        # self._column_categories = None
        # self._summary = None  # session -> data
        # self._targets = None
        #
        # self._all_feature_columns = None  # session -> all_features
        # self._feature_columns = None  # session -> features
        # self._feature_names = None
        #
        # self._train_size = None
        # self._split = None
        #
        # self.set_file(file)
        # self.set_name(name)
        # self.load_features()
        # self._base_path = self._file.replace(self._name + '.csv', '')


def _is_png(filename):
    return '.png' in filename


def _parse_function(filename, label):
    image_string = tf.read_file(filename)
    image_decoded = tf.image.decode_jpeg(image_string)
    return image_decoded, label


def dataset_from_files(filenames, labels):
    '''
    :param filenames: list of strings
    :param labels: list of integers
    :return: tf.data.Dataset
    '''

    filenames = tf.constant(filenames)

    # `labels[i]` is the label for the image in `filenames[i].
    labels = tf.constant(labels)

    dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
    dataset = dataset.map(_parse_function)
    return dataset


def dataset_from_array(array, labels):
    return tf.data.Dataset.from_tensor_slices((array, labels))


def find_image_files_folder_per_class(data_dir):
    folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]

    labels = []
    filenames = []
    class_names = []
    i = 0
    for f in folders:
        matching_files = tf.gfile.Glob('%s/%s/*.jpg' % (data_dir, f))
        matching_files += tf.gfile.Glob('%s/%s/*.jpeg' % (data_dir, f))
        n_images = len(matching_files)
        if n_images > 0:
            labels.extend([i] * n_images)
            class_names.append(f)
            filenames.extend(matching_files)
            i += 1

    assert (len(filenames) > 1 and len(set(labels)) > 1)
    dataset = dataset_from_files(filenames, labels)
    return dataset, class_names


def find_image_files_from_file(data_dir, info_file):
    info_file = pd.read_csv(info_file, sep=None, engine='python')
    # TODO Structure for now: col 0 =  im name, col 1 = label

    filenames = info_file[info_file.columns[0]].values
    if not os.path.isfile(filenames[0]):
        filenames = [os.path.join(data_dir, f) for f in filenames]
    class_names = list(info_file[info_file.columns[1]].unique())
    labels = info_file[info_file.columns[1]].values
    labels = [class_names.index(l) for l in labels]

    assert (len(filenames) > 1 and len(set(labels)) > 1)
    dataset = dataset_from_files(filenames, labels)
    return dataset, class_names
