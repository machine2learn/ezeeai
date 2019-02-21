import shutil
from abc import ABCMeta, abstractmethod

from scipy.misc import imresize

from data import tabular, image
from data.utils.image import find_image_files_folder_per_class, find_image_files_from_file, find_images_test_file
from io import BytesIO
from skimage.segmentation import mark_boundaries
from utils.explain_util import get_reg_explain, get_class_explain, clean_predict_table
from utils.request_util import *
from utils import feature_util, preprocessing, param_utils, run_utils, explain_util, sys_ops
from utils.sys_ops import unzip, tree_remove, find_dataset_from_numpy
import os
import pandas as pd
import dill as pickle
import cv2
import base64
import numpy as np
import PIL.Image


def encode_image(path):
    if isinstance(path, np.ndarray):
        pil_img = PIL.Image.fromarray(path.astype(np.uint8))
        buff = BytesIO()
        pil_img.save(buff, format="JPEG")
        return base64.b64encode(buff.getvalue()).decode()

    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode()


class Helper(metaclass=ABCMeta):
    def __init__(self, dataset):
        self._dataset = dataset
        self._canned_data = None
        self._cy_model = None

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

    @abstractmethod
    def test_upload(self, request):
        pass

    @abstractmethod
    def write_dataset(self, data_path):
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
            'has_test': self._dataset.get_test_file() is not None,
            'test_files': self._dataset.get_all_test_files()
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

    def test_upload(self, request):
        test_file = get_filename(request)
        try:
            test_filename = os.path.join(self._dataset.get_base_path(), 'test', test_file)
            df_test = sys_ops.bytestr2df(request.get_json()['file'], test_filename)
            sys_ops.check_df(df_test, self._dataset.get_df(), self._dataset.get_targets(), test_filename)
        except ValueError:
            os.remove(test_filename)
            return "The file contents are not valid."
        return "ok"

    def test_request(self, request):
        if 'filename' in request.get_json():
            test_filename = os.path.join(self._dataset.get_base_path(), 'test', get_filename(request))
        else:
            test_filename = self._dataset.get_test_file()[0] if isinstance(self._dataset.get_test_file(),
                                                                           list) else self._dataset.get_test_file()
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

    def explain_return(self, sess, request, result):

        new_features = self.get_new_features(request)
        targets = self.get_targets()
        params = {}
        params['data_type'] = 'tabular'
        params["features"] = {k: new_features[k] for k in new_features.keys() if k not in targets}
        if result.mode == 'regression':
            graphs, predict_table = get_reg_explain(result)
            params['type'] = 'regression'
        else:
            graphs, predict_table = get_class_explain(result)
            params['type'] = 'class'
        params['graphs'] = graphs
        params['predict_table'] = predict_table

        sess.set('explain_params', params)

    def get_df_test(self, df_test, has_targets):
        return df_test[self.get_targets()].values if has_targets else None


class Image(Helper):
    def __init__(self, dataset):
        if not isinstance(dataset, image.Image):
            raise TypeError(f'dataset must be Image, not {dataset.__class__}')
        super().__init__(dataset)

        self._example_image = None

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

    def get_input_shape(self):
        pass

    def process_targets_request(self, request):
        pass

    def generate_rest_call(self, pred):
        pass

    def get_num_outputs(self):
        return self._dataset.get_num_outputs()

    def get_dataset_params(self):
        return self._dataset.get_params()

    def get_dataset_name(self):
        return self._dataset.get_name()

    def get_data(self):
        size = self._dataset.get_image_size()
        unique, counts = np.unique(self._dataset.get_labels(), return_counts=True)
        counts = counts.astype(int).tolist()
        if size is not None:
            return {'height': size[0],
                    'width': size[1],
                    'data': self.get_labels_images(),
                    'n_channels': size[2],
                    'counts': dict(zip(unique, counts))}
        return {'height': self._dataset.get_sample().shape[0], 'width': self._dataset.get_sample().shape[1],
                'data': self.get_labels_images(), 'num_outputs': self._dataset.get_num_outputs(),
                'n_channels': self._dataset.get_sample().shape[2],
                'counts': dict(zip(unique, counts))}

    def get_targets(self):
        return self._dataset.get_targets()

    def get_target_labels(self):
        return self._dataset.get_class_names()

    def get_train_size(self):
        return self._dataset.get_train_size()

    def set_split(self, split):
        self._dataset.set_split(split)

    def get_mode(self):
        if self._dataset.get_class_names():
            return 'classification'
        return 'regression'

    def get_labels_images(self):
        data = {}
        class_names = self._dataset.get_class_names()
        labels = self._dataset.get_labels() if isinstance(self._dataset.get_labels(),
                                                          list) else self._dataset.get_labels().tolist()
        for c in class_names:
            data[str(c)] = {}
            im_path = self._dataset._images[labels.index(c)]
            data[str(c)]['img'] = encode_image(im_path)
            if self._dataset.get_mode() != 3:
                data[str(c)]['extension'] = im_path.split('.')[-1]
        return data

    def process_features_request(self, request):
        augmentation_options = request.get_json()['augmentation_options']
        features_params = request.get_json()['augmentation_params']

        self._dataset.set_normalization_method(request.get_json()['normalization'])
        h, w, c = self._dataset.get_sample().shape
        self._dataset.set_image_size(request.get_json()['height'], request.get_json()['width'], c)

        data = self.get_labels_images()

        data['input_shape'] = '[' + str(request.get_json()['height']) + ',' + str(
            request.get_json()['width']) + ',' + str(c) + ']'
        data['n_channels'] = c
        data['num_outputs'] = self._dataset.get_num_outputs()

        self._dataset.split_dataset(self._dataset.get_split())

        self._dataset.set_augmentation_params(features_params)
        self._dataset.set_augmentation_options(augmentation_options)
        return data

    def get_default_data_example(self):
        # TODO
        example = self._dataset._val_images[np.random.choice(np.arange(len(self._dataset._val_images)))]

        result = {
            'targets': self.get_targets(),
            'has_test': self._dataset._test_images is not None,
            'image': encode_image(example),
            'extension': example.split('.')[-1] if self._dataset.get_mode() != 3 else None,
            'test_files': self._dataset.get_all_test_files()
        }
        return result, False

    def get_new_features(self, request, default_features=False):
        b = request.files['inputFile'].read()
        request.files['inputFile'].seek(0)
        npimg = np.fromstring(b, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        return img.astype(np.float32)

    def process_explain_request(self, request):
        new_features = self.get_new_features(request)

        num_feat = get_num_feat(request)
        top_labels = get_top_labels(request)

        sel_target = get_sel_target(request)

        self._example_image = new_features

        ep = {
            'features': new_features,
            'num_features': num_feat,
            'top_labels': top_labels,
            'sel_target': sel_target
        }
        return ep

    def process_test_predict(self, df, final_pred, test_filenames):
        assert len(test_filenames) == len(final_pred['preds'])
        return sys_ops.save_image_results(df, final_pred['preds'], self._dataset.get_targets(), test_filenames,
                                          self._dataset.get_dataset_path().replace('train', ''))

    def test_request(self, request):
        has_targets = True
        df_test = {}
        test_filename = []
        labels = []
        if 'filename' in request.get_json():
            if get_filename(request) == 'TEST FROM SPLIT':
                test_filename = self._dataset.get_test_split_images()
                df_test = {self._dataset.get_targets()[0]: self._dataset.get_test_split_labels()}
            else:
                test_path = os.path.join(self._dataset.get_dataset_path().replace('train', 'test'),
                                         get_filename(request))
                option = [f for f in os.listdir(test_path) if f.startswith('.option')][0]

                if option == '.option0':
                    test_path = os.path.join(test_path, get_filename(request) + '.npz')
                    data = np.load(test_path)
                    test_filename = data['x']

                    if 'y' in data:
                        labels = data['y']
                        assert len(data['y'].shape) < 3  # TODO
                    else:
                        return False, test_filename, None, None
                elif option == '.option1':
                    test_filename = [os.path.join(test_path, t) for t in os.listdir(test_path) if not t.startswith('.')]
                    return False, test_filename, None, None

                elif option == '.option2':
                    all_classes = [c for c in os.listdir(test_path) if not c.startswith('.')]
                    for cl in all_classes:
                        list_files = [os.path.join(test_path, cl, f) for f in os.listdir(os.path.join(test_path, cl)) if
                                      not f.startswith('.')]
                        test_filename += list_files
                        labels += [cl] * len(list_files)

                elif option == '.option3':
                    labels_file = [os.path.join(test_path, t) for t in os.listdir(test_path) if t.startswith('labels.')]
                    test_filename, labels, _ = find_image_files_from_file(test_path, labels_file[0])
                df_test[self._dataset.get_targets()[0]] = labels
            return has_targets, test_filename, df_test, None
        return False

    def test_upload(self, request):
        test_file = request.files['input_file']
        filename = test_file.filename

        dataset_test_path = os.path.join(self._dataset.get_dataset_path().replace('train', 'test'),
                                         filename.split('.')[0])
        path_file = os.path.join(dataset_test_path, filename)
        os.makedirs(dataset_test_path, exist_ok=True)

        test_file.save(path_file)

        try:
            if path_file.endswith('.npz'):
                try:
                    _, test_data = find_dataset_from_numpy(path_file, requires_y=False, only_test=True)
                    if test_data is None:
                        tree_remove(dataset_test_path)
                        return 'The file contents are not valid.'
                    np.savez(path_file, x=test_data[0], y=test_data[1])
                    open(os.path.join(dataset_test_path, '.option0'), 'w')  # NUMPY FILE
                    return 'ok'
                except KeyError:
                    tree_remove(dataset_test_path)
                    return "The file contents are not valid."
            else:
                if not unzip(path_file, dataset_test_path):
                    return "The file contents already exists."

                os.remove(path_file)

                if find_images_test_file(dataset_test_path):
                    open(os.path.join(dataset_test_path, '.option1'), 'w')  # ONLY IMAGES
                else:
                    try:
                        f, n, c = find_image_files_folder_per_class(dataset_test_path, require_all=False)
                        assert len(c) == len(self.get_target_labels())
                        open(os.path.join(dataset_test_path, '.option2'), 'w')  # FOLDER PER CLASS
                    except AssertionError:
                        try:
                            info_file = [f for f in os.listdir(dataset_test_path) if
                                         f.startswith('test.') or f.startswith('labels.')]
                            assert len(info_file) == 1
                            info_path = os.path.join(dataset_test_path, info_file[0])
                            f, n, c = find_image_files_from_file(dataset_test_path, info_path, require_all=False)
                            assert len(c) == len(self.get_target_labels())
                            open(os.path.join(dataset_test_path, '.option3'), 'w')  # LABELS.TXT
                            os.rename(info_path, os.path.join(dataset_test_path, 'labels.txt'))

                        except AssertionError:
                            tree_remove(dataset_test_path)
                            return "The file contents are not valid."
        except ValueError:
            tree_remove(dataset_test_path)
            return "The file contents are not valid."
        return 'ok'

    def write_dataset(self, data_path):
        pickle.dump(self._dataset, open(data_path, 'wb'))

    def explain_return(self, sess, request, results):

        result, probs = results
        params = {}
        label = result.top_labels[0]
        num_features = get_num_feat(request)
        temp, mask = result.get_image_and_mask(label, positive_only=False, num_features=num_features, hide_rest=False)

        image = mark_boundaries(temp.astype(np.uint8), mask)

        params['data_type'] = 'image'
        params['type'] = 'class'
        params['features'] = encode_image((image * 255).astype(np.uint8))

        predict_table = {'columns': [], 'data': []}
        num_class = len(self._dataset.get_class_names())

        if num_class == 2:
            predict_table['columns'] = self._dataset.get_class_names()
            if result.local_pred[0] >= 0:
                predict_table['data'] = [float("{0:.3f}".format(1 - result.local_pred[0])),
                                         float("{0:.3f}".format(result.local_pred[0]))]
        else:
            predict_table['columns'] = self._dataset.get_class_names()
            predict_table['data'] = probs.tolist()

        params['predict_table'] = clean_predict_table(predict_table)
        params['graphs'] = None
        sess.set('explain_params', params)

    def get_df_test(self, df_test, has_targets):
        if not has_targets:
            return None
        return np.array([[f] for f in df_test[self.get_targets()[0]]])
