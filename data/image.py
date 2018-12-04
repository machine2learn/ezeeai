import tensorflow as tf
import os
import pandas as pd
import numpy as np
import cv2
from utils import args
from sklearn.model_selection import train_test_split


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
    # dataset = dataset.map(_parse_function)
    return dataset


def dataset_from_array(array, labels):
    return tf.data.Dataset.from_tensor_slices((array, labels))


def find_image_files_folder_per_class(data_dir):
    folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]

    labels = []
    filenames = []
    class_names = []
    for f in folders:
        matching_files = tf.gfile.Glob('%s/%s/*.jpg' % (data_dir, f))
        matching_files += tf.gfile.Glob('%s/%s/*.jpeg' % (data_dir, f))  # TODO accept more types
        n_images = len(matching_files)
        if n_images > 0:
            labels.extend([f] * n_images)
            class_names.append(f)
            filenames.extend(matching_files)
    assert (len(filenames) > 1 and len(set(labels)) > 1)

    return filenames, labels, class_names


def find_image_files_from_file(data_dir, info_file):
    info_file = pd.read_csv(info_file, sep=None, engine='python')
    # TODO Structure for now: col 0 =  im name, col 1 = label

    filenames = info_file[info_file.columns[0]].values
    if not os.path.isfile(filenames[0]):
        filenames = [os.path.join(data_dir, f) for f in filenames]
    class_names = list(info_file[info_file.columns[1]].unique())
    labels = info_file[info_file.columns[1]].values
    labels = labels.astype('object')

    assert (len(filenames) > 1 and len(set(labels)) > 1)
    return filenames, labels, class_names


def read_numpy_array(path_file):
    data = np.load(path_file)
    x, y = data['x'], data['y']
    return x, y, [str(x) for x in np.unique(y)]


class Image:
    def __init__(self, dataset_path, mode, name):
        self._name = name
        self._dataset_path = dataset_path
        self._mode = mode
        self._images = None
        self._labels = None
        self._class_names = None
        self._train_size = None
        self._split = None

        self._read_data()
        self._train_images = self._val_images = self._test_images = self._train_labels = self._val_labels = self._test_labels = None

        self._normalization_method = None
        self._image_size = None
        self._augmentation_options = None
        self._augmentation_params = None

    def set_augmentation_options(self, opts):
        self._augmentation_options = opts

    def get_augmentation_options(self):
        return self._augmentation_options

    def set_augmentation_params(self, p):
        self._augmentation_params = p

    def get_augmentation_params(self):
        return self._augmentation_params

    def get_class_names(self):
        return self._class_names

    def set_normalization_method(self, norm):
        args.assert_type(str, norm)
        self._normalization_method = norm

    def get_normalization_method(self):
        return self._normalization_method

    def set_image_size(self, height, width):
        self._image_size = [int(height), int(width)]

    def get_image_size(self):
        return self._image_size

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

    def get_labels(self):
        return self._labels

    def _read_data(self):
        if self.get_mode() == 1:
            self._images, self._labels, self._class_names = find_image_files_folder_per_class(self.get_dataset_path())
        elif self.get_mode() == 2:
            info_file = [f for f in os.listdir(self.get_dataset_path()) if f.startswith('labels.')]
            self._images, self._labels, self._class_names = find_image_files_from_file(self.get_dataset_path(),
                                                                                       os.path.join(
                                                                                           self.get_dataset_path(),
                                                                                           info_file[0]))
        elif self.get_mode() == 3:
            npz_file = [f for f in os.listdir(self.get_dataset_path()) if f.endswith('.npz')]
            self._images, self._labels, self._class_names = read_numpy_array(
                os.path.join(self.get_dataset_path(), npz_file[0]))

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
        self._train_size = len(self._train_images)

    def get_sample(self):
        if self.get_mode() == 3:
            return self._images[0]
        return cv2.imread(self._images[0])

    def get_num_outputs(self):
        num_classes = len(self.get_class_names())
        if num_classes > 2:
            return num_classes
        return 1

    def get_params(self):
        return {'name': self.get_name(),
                'split': self.get_split(),
                'normalization': self.get_normalization_method(),
                'height': self.get_image_size()[0],
                'width': self.get_image_size()[1],
                'augmentation_options': self.get_augmentation_options(),
                'augmentation_params': self.get_augmentation_params()
                }

    def get_targets(self):
        return ['class']

    def get_target_labels(self):
        return self.get_class_names()

    def get_train_size(self):
        return self._train_size

    def _parse_function(self, image, label):
        if self.get_mode() != 3:
            image_string = tf.read_file(image)
            image = tf.image.decode_jpeg(image_string)
        image_decoded = tf.cast(image, tf.float32)
        # TODO normalization
        return tf.image.resize_images(image_decoded, self.get_image_size().copy().re), label

    def train_input_fn(self, batch_size, num_epochs):
        if self.get_mode() == 3:
            dataset = dataset_from_array(self._train_images, self._train_labels)
        else:
            dataset = dataset_from_files(self._train_images, self._train_labels)

        dataset = dataset.shuffle(len(self._train_images)).repeat(num_epochs).map(self._parse_function).batch(
            batch_size)

        # dataset = dataset.map(self._parse_function)
        # dataset = dataset.prefetch(buffer_size) TODO
        # TODO DATA AUGMENTATION
        return dataset

    def validation_input_fn(self, batch_size):
        if self.get_mode() == 3:
            dataset = dataset_from_array(self._val_images, self._val_labels)
        else:
            dataset = dataset_from_files(self._val_images, self._val_labels)
        dataset = dataset.map(self._parse_function).batch(batch_size)
        return dataset

    def test_input_fn(self, batch_size, file=None):
        # file = file or self.get_test_file()[0] if isinstance(self.get_test_file(),
        #                                                      list) else self.get_test_file()  # TODO
        # csv_dataset = make_csv_dataset([file], batch_size=batch_size, shuffle=False,
        #                                label_names=self.get_targets(), num_epochs=1,
        #                                column_defaults=self.get_converted_defaults())
        # return csv_dataset
        pass

    def input_predict_fn(self, image):
        size = self.get_image_size().copy()
        size.reverse()

        image = cv2.resize(image, tuple(size))
        #TODO normalization
        return tf.estimator.inputs.numpy_input_fn(x=image, y=None, num_epochs=1, shuffle=False)

    def serving_input_receiver_fn(self):
        h, w, c = self.get_sample().shape
        receiver_tensors = tf.placeholder(tf.float32, [None, None, None, c])
        return tf.estimator.export.ServingInputReceiver(receiver_tensors=receiver_tensors,
                                                        features=receiver_tensors)
