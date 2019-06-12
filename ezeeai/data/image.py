
from ezeeai.data.utils.image import *
from ..utils import args
from sklearn.model_selection import train_test_split
from scipy.misc import imresize


class Image:
    def __init__(self, dataset_path, test_path, mode, name):
        self._name = name
        self._dataset_path = dataset_path
        self._test_path = test_path
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
        self._n_channels = None

    def get_test_path(self):
        return self._test_path

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

    def set_image_size(self, height, width, nc):
        self._image_size = [int(height), int(width), int(nc)]

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

    def split_dataset(self, percent=None, save=True):
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
        _, _, self._n_channels = self.get_sample().shape

    def get_sample(self):
        from scipy.misc import imread
        if self.get_mode() == 3:
            return self._images[0]
        img = imread(self._images[0])
        return img

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

    def _parse_function(self, image, label=None):
        if self.get_mode() != 3:
            image_string = tf.read_file(image)
            image = tf.image.decode_jpeg(image_string)
        image_decoded = tf.cast(image, tf.float32)
        size = self.get_image_size().copy()
        if len(size) > 2:
            size = size[0:2]

        if label is not None:
            return tf.image.resize_images(image_decoded, size), label
        return tf.image.resize_images(image_decoded, size)

    def _norm_function(self, image, label=None):
        image = norm_tf_options[self.get_normalization_method()](image)
        if label is not None:
            return image, label
        return image

    def _parse_augmentation_options(self, image, label):
        params = self.get_augmentation_params()
        options = self.get_augmentation_options()

        if 'flip' in options:
            if params['horizontal_flip']:
                image = tf.image.random_flip_left_right(image)
            if params['vertical_flip']:
                image = tf.image.random_flip_up_down(image)
        if 'rotation' in options:
            interpolation = 'NEAREST' if params['interpolation_rotation_nearest'] else 'BILINEAR'
            angle = tf.random_uniform([], minval=float(params['angle_from_rotation']),
                                      maxval=float(params['angle_to_rotation']))
            image = tf.contrib.image.rotate(image, angle, interpolation=interpolation)
        if 'saturation' in options:
            image = tf.image.random_saturation(image, float(params['from_saturation']), float(params['to_saturation']))
        if 'contrast' in options:
            image = tf.image.random_contrast(image, float(params['from_contrast']), float(params['to_contrast']))
        if 'brightness' in options:
            image = tf.image.random_brightness(image, float(params['max_delta_brightness']))
        if 'randomhue' in options:
            image = tf.image.random_hue(image, float(params['max_delta_randomhue']))
        if 'quality' in options:
            image = tf.image.random_jpeg_quality(image, int(params['from_quality']), int(params['to_quality']))

        if 'zoom' in options:
            image = random_central_crop(image, float(params['from_zoom']), float(params['to_zoom']))
            image = tf.image.resize_images(image, self.get_image_size().copy()[:2])

        return image, label

    def train_input_fn(self, batch_size, num_epochs):
        if self.get_mode() == 3:
            dataset = dataset_from_array(self._train_images, self._train_labels)
        else:
            dataset = dataset_from_files(self._train_images, self._train_labels)

        dataset = dataset.shuffle(len(self._train_images)).repeat(num_epochs).map(self._parse_function).map(
            self._parse_augmentation_options).map(self._norm_function).batch(batch_size)

        dataset = dataset.prefetch(1)
        return dataset

    def validation_input_fn(self, batch_size):
        if self.get_mode() == 3:
            dataset = dataset_from_array(self._val_images, self._val_labels)
        else:
            dataset = dataset_from_files(self._val_images, self._val_labels)
        dataset = dataset.map(self._parse_function).map(self._norm_function).batch(batch_size)
        dataset = dataset.prefetch(1)
        return dataset

    def test_input_fn(self, batch_size, file=None):
        if self.get_mode() == 3:
            if file is not None:
                dataset = dataset_from_array(file)
            else:
                dataset = dataset_from_array(self._test_images, self._test_labels)

        else:
            if file is not None:
                dataset = dataset_from_files(file)
            else:
                dataset = dataset_from_files(self._test_images, self._test_labels)
        dataset = dataset.map(self._parse_function).map(self._norm_function).batch(batch_size)
        dataset = dataset.prefetch(1)
        return dataset

    def input_predict_fn(self, image):
        image = imresize(image, self.get_image_size(), interp='bilinear')
        image = image.astype(np.float32)
        if len(image.shape) == 3:
            image = image[np.newaxis, ...]
        # TODO normalization
        image = norm_options[self.get_normalization_method()](image)

        return tf.estimator.inputs.numpy_input_fn(x=image, y=None, num_epochs=1, shuffle=False)

    def serving_input_receiver_fn(self):
        receiver_tensors = tf.placeholder(tf.float32, [None, None, None, self._n_channels])
        return tf.estimator.export.ServingInputReceiver(receiver_tensors=receiver_tensors,
                                                        features=receiver_tensors)

    def normalize(self, image):
        return norm_options[self.get_normalization_method()](image)

    def get_all_test_files(self):
        test_path = self.get_dataset_path().replace('train', 'test')
        try:
            return [name for name in os.listdir(test_path) if os.path.isdir(os.path.join(test_path, name))]
        except ValueError:
            return []

    def get_test_split_images(self):
        return self._test_images

    def get_test_split_labels(self):
        return self._test_labels
