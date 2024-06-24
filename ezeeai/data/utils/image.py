import os

import numpy as np
import pandas as pd
from tensorflow.python import ops
from tensorflow.python.ops import array_ops, math_ops
from tensorflow.python.ops.image_ops_impl import _AssertAtLeast3DImage
from ezeeai.utils.preprocessing import has_header
import tensorflow as tf


def random_central_crop(image, minval, maxval):
    with ops.name_scope(None, 'central_crop', [image]):
        image = ops.convert_to_tensor(image, name='image')

        if (minval < 0 or maxval < 0 or
                minval > 1 or maxval > 1):
            raise ValueError('crop ratio range must be between 0 and 1.')

        _AssertAtLeast3DImage(image)
        rank = image.get_shape().ndims
        if rank != 3 and rank != 4:
            raise ValueError('`image` should either be a Tensor with rank = 3 or '
                             'rank = 4. Had rank = {}.'.format(rank))

        # Helper method to return the `idx`-th dimension of `tensor`, along with
        # a boolean signifying if the dimension is dynamic.
        def _get_dim(tensor, idx):
            static_shape = tensor.get_shape()[idx].value
            if static_shape is not None:
                return static_shape, False
            return array_ops.shape(tensor)[idx], True

        # Get the height, width, depth (and batch size, if the image is a 4-D
        # tensor).
        if rank == 3:
            img_h, dynamic_h = _get_dim(image, 0)
            img_w, dynamic_w = _get_dim(image, 1)
            img_d = image.get_shape()[2]
        else:
            img_bs = image.get_shape()[0]
            img_h, dynamic_h = _get_dim(image, 1)
            img_w, dynamic_w = _get_dim(image, 2)
            img_d = image.get_shape()[3]

        central_fraction = tf.random.uniform([], minval=minval, maxval=maxval, dtype=tf.float64)

        # Compute the bounding boxes for the crop. The type and value of the
        # bounding boxes depend on the `image` tensor's rank and whether / not the
        # dimensions are statically defined.
        img_hd = math_ops.to_double(img_h)
        bbox_h_start = math_ops.to_int32((img_hd - img_hd * central_fraction) / 2)

        img_wd = math_ops.to_double(img_w)
        bbox_w_start = math_ops.to_int32((img_wd - img_wd * central_fraction) / 2)

        bbox_h_size = img_h - bbox_h_start * 2
        bbox_w_size = img_w - bbox_w_start * 2

        if rank == 3:
            bbox_begin = array_ops.stack([bbox_h_start, bbox_w_start, 0])
            bbox_size = array_ops.stack([bbox_h_size, bbox_w_size, -1])
        else:
            bbox_begin = array_ops.stack([0, bbox_h_start, bbox_w_start, 0])
            bbox_size = array_ops.stack([-1, bbox_h_size, bbox_w_size, -1])

        image = array_ops.slice(image, bbox_begin, bbox_size)

        # Reshape the `image` tensor to the desired size.
        if rank == 3:
            image.set_shape([
                None,
                None,
                img_d
            ])
        else:
            image.set_shape([
                img_bs,
                None,
                None,
                img_d
            ])
        return image


def zeroCenter(x):
    x /= 255.
    x -= 0.5
    x *= 2.
    return x


def mean_std(x):
    def relu(v):
        return max(0, v)

    image_mean = np.mean(x)
    num_pixels = x.size
    variance = (np.mean(np.square(x)) - np.square(image_mean))
    variance = relu(variance)
    stddev = np.sqrt(variance)
    min_stddev = 1 / np.sqrt(num_pixels)
    pixel_value_scale = np.maximum(stddev, min_stddev)
    pixel_value_offset = image_mean
    return pixel_value_offset, pixel_value_scale


def per_image_standardization(x):
    mean, adjusted_stddev = mean_std(x)
    return (x - mean) / adjusted_stddev


MEANS = np.array([123.68, 116.779, 103.939]).astype(np.float32)  # BGR
norm_options = {"unit_length": lambda x: x / 255,
                "per_image": per_image_standardization,
                "zero_center": zeroCenter,
                "imagenet_mean_subtraction": lambda x: x - MEANS}
norm_tf_options = {"unit_length": lambda x: x / 255,
                   "per_image": tf.image.per_image_standardization,
                   "zero_center": zeroCenter,
                   "imagenet_mean_subtraction": lambda x: x - MEANS}


def dataset_from_files(filenames, labels=None):
    '''
    :param filenames: list of strings
    :param labels: list of integers
    :return: tf.data.Dataset
    '''

    filenames = tf.constant(filenames)

    if labels is not None:
        # `labels[i]` is the label for the image in `filenames[i].
        labels = tf.constant(labels)

        dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
        # dataset = dataset.map(_parse_function)
    else:
        dataset = tf.data.Dataset.from_tensor_slices(filenames)
    return dataset


def dataset_from_array(array, labels=None):
    if labels is not None:
        return tf.data.Dataset.from_tensor_slices((array, labels))
    return tf.data.Dataset.from_tensor_slices(array)


def find_image_files_folder_per_class(data_dir, require_all=True):
    folders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]

    labels = []
    filenames = []
    class_names = []
    for f in folders:
        matching_files = []
        for ext in ['jpg', 'jpeg', 'png', 'PNG', 'JPG', 'JPEG']:
            matching_files += tf.io.gfile.glob('%s/%s/*.%s' % (data_dir, f, ext))
        n_images = len(matching_files)
        if n_images > 0:
            labels.extend([f] * n_images)
            class_names.append(f)
            filenames.extend(matching_files)

    if require_all:
        assert (len(filenames) > 1 and len(set(labels)) > 1)

    return filenames, labels, class_names


def find_image_files_from_file(data_dir, info_file, require_all=True):
    args = {}
    if not has_header(info_file):
        args['header'] = None

    info_file = pd.read_csv(info_file, sep=None, engine='python', **args)


    filenames = info_file[info_file.columns[0]].values
    if not os.path.isfile(filenames[0]):
        filenames = [os.path.join(data_dir, f) for f in filenames]
    class_names = list(info_file[info_file.columns[1]].unique())
    labels = info_file[info_file.columns[1]].values
    labels = labels.astype('object')
    if require_all:
        assert (len(filenames) > 1 and len(set(labels)) > 1)
    return filenames, labels, class_names


def find_images_test_file(path):
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            if os.path.splitext(os.path.join(path, f))[1] not in ['.jpg', '.jpeg', '.png', '.PNG', '.JPG', '.JPEG']:
                return False
        else:
            return False
    return True


def read_numpy_array(path_file):
    data = np.load(path_file)
    x, y = data['x'], data['y']
    return x, [str(i) for i in y], [str(i) for i in np.unique(y)]
