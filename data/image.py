import tensorflow as tf
import os
import pandas as pd
import numpy as np
import cv2
from utils import args
from sklearn.model_selection import train_test_split


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
    # dataset = dataset_from_files(filenames, labels)
    return filenames, labels


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
    # dataset = dataset_from_files(filenames, labels)
    return filenames, labels


def read_numpy_array(path_file):
    data = np.load(path_file)
    x, y = data['x'], data['y']
    return x, y


class Image:
    def __init__(self, dataset_path, mode, name):
        self._name = name
        self._dataset_path = dataset_path
        self._mode = mode
        self._images = None
        self._labels = None

        self._train_size = None
        self._split = None

        self._read_data()
        self._train_images = self._val_images = self._test_images = self._train_labels = self._val_labels = self._test_labels = None

    def set_name(self, name):
        args.assert_type(str, name)
        self._name = name

    def get_name(self):
        return self._name

    def get_mode(self):
        return self._mode

    def get_dataset_path(self):
        return self._dataset_path

    def get_split(self):
        return self._split

    def set_split(self, split):
        args.assert_type(str, split)
        self._split = split

    def _read_data(self):
        if self.get_mode() == 1:
            self._images, self._labels = find_image_files_folder_per_class(self.get_dataset_path())
        elif self.get_mode() == 2:
            info_file = [f for f in os.listdir(self.get_dataset_path()) if f.startswith('labels.')]
            self._images, self._labels = find_image_files_from_file(self.get_dataset_path(),
                                                                    os.path.join(self.get_dataset_path(), info_file[0]))
        elif self.get_mode() == 3:
            npz_file = [f for f in os.listdir(self.get_dataset_path()) if f.endswith('.npz')]
            self._images, self._labels = read_numpy_array(os.path.join(self.get_dataset_path(), npz_file[0]))

    def split_dataset(self, percent=None):
        percent = percent or self.get_split()
        self.set_split(percent)

        percent = percent.split(',')
        percent = (int(percent[0]), int(percent[1]), int(percent[2]))
        # TODO split filename list or numpy array

        # stratify = None
        val_frac = percent[1] / 100

        self._train_images, self._val_images, self._train_labels, self._val_labels = train_test_split(
            self._images, self._labels, test_size=val_frac, stratify=self._labels, random_state=42)

        if percent[2] != 0:
            test_size = int(round((percent[2] / 100) * len(self._images)))
            self._train_images, self._test_images, self._train_labels, self._test_labels = train_test_split(
                self._train_images, self._train_labels, test_size=test_size, stratify=self._train_labels,
                random_state=42)

    def get_sample(self):
        if self.get_mode() == 3:
            return self._images[0]
        return cv2.imread(self._images[0])
