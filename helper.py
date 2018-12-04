import cv2
from abc import ABCMeta, abstractmethod

from data import tabular, image
from data.image import find_image_files_folder_per_class, find_image_files_from_file
from utils.request_util import *
from utils import feature_util, preprocessing, param_utils, run_utils, explain_util, sys_ops

import os
import pandas as pd
import dill as pickle

import base64
import numpy as np


def encode_image(path):
    if isinstance(path, np.ndarray):
        return base64.b64encode(path).decode()

    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode()


class Helper(metaclass=ABCMeta):
    def __init__(self, dataset):
        self._dataset = dataset

    @abstractmethod
    def get_num_outputs(self):
        pass

    @abstractmethod
    def get_input_shape(self):
        pass

    @abstractmethod
    def get_dataset_params(self):
        pass

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def get_dataset_name(self):
        pass

    @abstractmethod
    def get_targets(self):
        pass

    @abstractmethod
    def get_target_labels(self):
        pass

    @abstractmethod
    def get_train_size(self):
        pass

    @abstractmethod
    def set_split(self, split):
        pass

    @abstractmethod
    def process_features_request(self, request):
        pass

    @abstractmethod
    def process_targets_request(self, request):
        pass

    @abstractmethod
    def get_default_data_example(self):
        pass

    @abstractmethod
    def get_new_features(self, form, default_features=False):
        pass

    @abstractmethod
    def process_explain_request(self, request):
        pass

    @abstractmethod
    def generate_rest_call(self, pred):
        pass

    @abstractmethod
    def test_request(self, request):
        pass

    @abstractmethod
    def process_test_predict(self, df, final_pred, test_filename):
        pass


class Tabular(Helper):
    def __init__(self, dataset):
        if not isinstance(dataset, tabular.Tabular):
            raise TypeError(f'dataset must be Tabular, not {dataset.__class__}')
        super().__init__(dataset)

    def get_num_outputs(self):
        return self._dataset.get_num_outputs()

    def get_input_shape(self):
        return self._dataset.get_num_inputs()

    def get_dataset_params(self):
        return self._dataset.get_params()

    def get_dataset_name(self):
        return self._dataset.get_name()

    def get_data(self):
        return self._dataset.get_data_summary().to_json()

    def get_targets(self):
        return self._dataset.get_targets()

    def get_target_labels(self):
        return self._dataset.get_target_labels()

    def get_train_size(self):
        return self._dataset.get_train_size()

    def set_split(self, split):
        self._dataset.set_split(split)

    def process_features_request(self, request):
        ds = self._dataset.get_data_summary()
        self._dataset.set_normalize(get_normalize(request))
        cat_columns, default_values = feature_util.reorder_request(get_default_feature(request),
                                                                   get_cat_columns(request),
                                                                   get_default_columns(request),
                                                                   self._dataset.get_df().keys())
        self._dataset.update_features(cat_columns, default_values)
        data = ds[(ds.Category != 'hash') & (ds.Category != 'none')]
        return {'data': data.to_json(),
                'old_targets': self._dataset.get_targets() or []}

    def process_targets_request(self, request):
        selected_rows = get_targets(request)

        if not self._dataset.update_targets(selected_rows):
            return {'error': 'Only numerical features are supported for multiouput.'}

        self._dataset.split_dataset()
        self._dataset.split_dataset()
        self._dataset.update_feature_columns()  # TODO maybe inside split

        if not preprocessing.check_train(self._dataset.get_train_file(),
                                         self._dataset.get_targets()):  # TODO move to type-tabular
            return {'error': 'Number of classes for the target should be greater than 1.'}

        num_outputs = self.get_num_outputs()
        input_shape = self.get_input_shape()
        hidden_layers = param_utils.get_hidden_layers(input_shape, num_outputs, self._dataset.get_train_size())
        result = {
            'error': False,
            'num_outputs': num_outputs,
            'input_shape': '[' + str(input_shape) + ']',
            'hidden_layers': hidden_layers
        }
        return result

    def get_default_data_example(self):
        dict_types, categoricals = run_utils.get_dictionaries(self._dataset.get_defaults(),
                                                              self._dataset.get_categories(),
                                                              self._dataset.get_feature_selection(),
                                                              self._dataset.get_targets())
        sfeatures = feature_util.remove_targets(self._dataset.get_defaults(), self._dataset.get_targets())
        explain_disabled = run_utils.get_explain_disabled(self._dataset.get_categories())

        result = {
            'features': sfeatures,
            'types': run_utils.get_html_types(dict_types),
            'categoricals': categoricals,
            'targets': self._dataset.get_targets(),
            'has_test': self._dataset.get_test_file() is not None
        }

        return result, explain_disabled

    def get_new_features(self, request, default_features=False):
        return self._dataset.get_new_features(request.form) if not default_features else self._dataset.get_defaults()

    def process_explain_request(self, request):
        new_features = self.get_new_features(request)
        labels = self._dataset.get_target_labels()

        num_feat = get_num_feat(request)
        top_labels = get_top_labels(request)
        input_check = explain_util.check_input(num_feat, top_labels, len(new_features),
                                               1 if labels is None else len(labels))
        if input_check is not None:
            return {'explanation': input_check}

        sel_target = get_sel_target(request)
        ep = {
            'features': new_features,
            'num_features': num_feat,
            'top_labels': top_labels,
            'sel_target': sel_target
        }
        return ep

    def generate_rest_call(self, pred):
        call, d, epred = sys_ops.gen_example(self._dataset.get_targets(), self._dataset.get_data_summary(),
                                             self._dataset.get_df(),
                                             'model_name', pred)
        example = {'curl': call, 'd': d, 'output': epred}
        return example

    def create_ice_data(self, request):
        file_path, unique_val_column = explain_util.generate_ice_df(request,
                                                                    self._dataset.get_df(),
                                                                    self._dataset.get_file(),
                                                                    self._dataset.get_targets(),
                                                                    self._dataset.get_dtypes())
        return file_path, unique_val_column

    def process_ice_request(self, request, unique_val_column, pred):
        exp_target = request.get_json()['exp_target']
        exp_feature = request.get_json()['explain_feature']
        lab, probs = explain_util.get_exp_target_prediction(self._dataset.get_targets(), exp_target, pred,
                                                            self._dataset.get_dtypes())
        data = {exp_feature: unique_val_column,
                exp_target: lab,
                exp_target + '_prob': probs}

        return data

    def test_request(self, request):
        if 'filename' in request.get_json():
            test_file = get_filename(request)
            try:
                test_filename = os.path.join(self._dataset.get_base_path(), 'test', test_file)
                df_test = sys_ops.bytestr2df(request.get_json()['file'], test_filename)
                has_targets = sys_ops.check_df(df_test, self._dataset.get_df(), self._dataset.get_targets(),
                                               test_filename)
            except ValueError:
                return False, None, None, "The file contents are not valid."
        else:
            test_filename = self._dataset.get_test_file()[0] if isinstance(self._dataset.get_test_file(),
                                                                           list) else self._dataset.get_test_file()  # TODO
            has_targets = True
            df_test = pd.read_csv(test_filename)
        return has_targets, test_filename, df_test, None

    def process_test_predict(self, df, final_pred, test_filename):
        return sys_ops.save_results(df, final_pred['preds'], self._dataset.get_targets(), test_filename.split('/')[-1],
                                    self._dataset.get_base_path())

    def write_dataset(self, data_path):
        pickle.dump(self._dataset, open(data_path, 'wb'))

    def get_mode(self):
        return self._dataset.get_mode()


class Image(Helper):
    def __init__(self, dataset):
        if not isinstance(dataset, image.Image):
            raise TypeError(f'dataset must be Image, not {dataset.__class__}')
        super().__init__(dataset)

    @staticmethod
    def extract_dataset(option, file_path):
        data_dir = ''
        info_file = ''
        if option == 'option1':
            try:
                find_image_files_folder_per_class(data_dir)
            except AssertionError:
                return False
        elif option == 'option2':
            try:
                find_image_files_from_file(data_dir, info_file)
            except AssertionError:
                return False
        elif option == 'option3':
            pass
        return True

    def get_num_outputs(self):
        return self._dataset.get_num_outputs()

    def get_input_shape(self):
        pass

    def get_dataset_params(self):
        return self._dataset.get_params()

    def get_dataset_name(self):
        return self._dataset.get_name()

    def get_data(self):
        sample = self._dataset.get_sample()
        return {'height': sample.shape[0], 'width': sample.shape[1]}

    def get_targets(self):
        return self._dataset.get_targets()

    def get_target_labels(self):
        pass

    def get_train_size(self):
        return self._dataset.get_train_size()

    def set_split(self, split):
        self._dataset.set_split(split)

    def get_mode(self):
        if self._dataset.get_class_names():
            return 'classification'
        return 'regression'

    def process_features_request(self, request):
        augmentation_options = request.get_json()['augmentation_options']
        features_params = request.get_json()['augmentation_params']

        # TODO augmentation
        self._dataset.set_normalization_method(features_params['normalization'])
        self._dataset.set_image_size(features_params['height'], features_params['width'])
        data = {}
        class_names = self._dataset.get_class_names()
        labels = self._dataset.get_labels() if isinstance(self._dataset.get_labels(),
                                                          list) else self._dataset.get_labels().tolist()
        for c in class_names:
            data[c] = {}
            im_path = self._dataset._images[labels.index(c)]
            data[c]['img'] = encode_image(im_path)
            if self._dataset.get_mode() != 3:
                data[c]['extension'] = im_path.split('.')[-1]

        h, w, c = self._dataset.get_sample().shape
        data['input_shape'] = '[' + features_params['height'] + ',' + features_params['width'] + ',' + str(c) + ']'
        data['num_outputs'] = self._dataset.get_num_outputs()

        self._dataset.split_dataset(self._dataset.get_split())
        del features_params['normalization']
        del features_params['height']
        del features_params['width']
        self._dataset.set_augmentation_params(features_params)
        self._dataset.set_augmentation_options(augmentation_options)
        return data

    def process_targets_request(self, request):
        pass

    def get_default_data_example(self):
        # TODO
        example = np.random.choice(self._dataset._images)
        result = {
            'targets': self.get_targets(),
            'has_test': self._dataset._test_images is not None,
            'image': encode_image(example),
            'extension': example.split('.')[-1] if self._dataset.get_mode() != 3 else None
        }
        return result, False

    def get_new_features(self, request, default_features=False):
        b = request.files['inputFile'].read()
        npimg = np.fromstring(b, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        return img.astype(np.float32)

    def process_explain_request(self, request):
        new_features = self.get_new_features(request)

        num_feat = get_num_feat(request)
        top_labels = get_top_labels(request)

        sel_target = get_sel_target(request)
        ep = {
            'features': new_features,
            'num_features': num_feat,
            'top_labels': top_labels,
            'sel_target': sel_target
        }
        return ep

    def generate_rest_call(self, pred):
        pass

    def process_test_predict(self, df, final_pred, test_filename):
        pass

    def test_request(self, request):
        pass

    def write_dataset(self, data_path):
        pickle.dump(self._dataset, open(data_path, 'wb'))
