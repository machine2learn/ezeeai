import dill as pickle
from abc import ABCMeta

import tensorflow as tf
import shutil
import numpy as np
import logging
import os

import inspect

from GPUtil import GPUtil

from easyai.data.tabular import Tabular
from .model_builder import ModelBuilder
from ..extensions.best_exporter import BestExporter
from ..explainer import TabularExplainer, ImageExplainer
from easyai.utils.email_ops import send_email
from easyai.utils.run_utils import check_exports


HIDDEN_LAYERS = 'hidden_layers'

MAX_STEPS = 'max_steps'

KEEP_CHECKPOINT_MAX = 'keep_checkpoint_max'

SAVE_SUMMARY_STEPS = 'save_summary_steps'

SAVE_CHECKPOINTS_STEPS = 'save_checkpoints_steps'

optimizer_map = {'Adagrad': tf.train.AdagradOptimizer,
                 'Adam': tf.train.AdamOptimizer,
                 'Ftrl': tf.train.FtrlOptimizer,
                 'RMSProp': tf.train.RMSPropOptimizer,
                 'SGD': tf.train.GradientDescentOptimizer}


class AbstractEstimator(metaclass=ABCMeta):
    def __init__(self, params):
        self.dataset = pickle.load(open(params['data_path'], 'rb'))
        self.params = params
        self.checkpoint_dir = params['checkpoint_dir']
        # self.feature_columns = self.dataset.get_feature_columns()
        # self.feature_names = feature_util.get_feature_names(self.feature_columns)
        self.model = None
        self.max_steps = np.ceil(self.dataset.get_train_size() / int(params["batch_size"])) * int(params["num_epochs"])
        self.test_file = ''

        tf.logging.set_verbosity(tf.logging.DEBUG)
        log = logging.getLogger('tensorflow')
        log.setLevel(logging.ERROR)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(message)s')

        # create file handler which logs even debug messages
        fh = logging.FileHandler(os.path.join(params['log_dir'], 'tensorflow.log'))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        log.addHandler(fh)

        tf.reset_default_graph()
        if len(check_exports(params['export_dir'])) == 0:
            self.clear_checkpoint()

        self._create_run_config()
        self._create_model()
        self._create_specs()

    def _create_run_config(self):
        save_checkpoints_steps = self.params[SAVE_CHECKPOINTS_STEPS]
        save_summary_steps = self.params[SAVE_SUMMARY_STEPS]
        keep_checkpoint_max = self.params[KEEP_CHECKPOINT_MAX]

        gpu_options = tf.GPUOptions(allow_growth=True)
        config = tf.ConfigProto(gpu_options=gpu_options)
        f = [s.function for s in inspect.stack() if
             s.filename.split('/')[-1] == 'dfweb.py' and s.function != 'check_session'][-1]

        if f == 'predict' or (f != 'run' and len(GPUtil.getAvailable()) == 0):
            config.device_count.update({'GPU': 0})

        self.runConfig = tf.estimator.RunConfig(model_dir=self.checkpoint_dir,
                                                save_checkpoints_steps=save_checkpoints_steps,
                                                save_summary_steps=save_summary_steps,
                                                keep_checkpoint_max=keep_checkpoint_max,
                                                session_config=config)

    def _create_model(self):
        mb = ModelBuilder()
        self.params['config'] = self.runConfig

        if 'canned_data' in self.params:
            self.model = mb.create_from_canned(self.params)
        else:
            self.params['model_path'] = os.path.join(self.params['custom_path'], 'model_tfjs.json')
            self.model = mb.create_from_keras(self.params)

    def _create_specs(self):

        self.train_spec = tf.estimator.TrainSpec(
            input_fn=self._train_input_fn, max_steps=self.max_steps)

        self.eval_spec = tf.estimator.EvalSpec(
            input_fn=self._validation_input_fn,
            steps=None,  # How many batches of test data
            exporters=BestExporter(serving_input_receiver_fn=self.dataset.serving_input_receiver_fn,
                                   exports_to_keep=self.params[KEEP_CHECKPOINT_MAX]),
            start_delay_secs=0, throttle_secs=1)

    def _train_input_fn(self):
        return self.dataset.train_input_fn(int(self.params["batch_size"]), int(self.params['num_epochs']))

    def _validation_input_fn(self):
        return self.dataset.validation_input_fn(int(self.params["batch_size"]))

    def _test_input_fn(self):
        return self.dataset.test_input_fn(int(self.params["batch_size"]), self.test_file)

    def clear_checkpoint(self):
        shutil.rmtree(self.checkpoint_dir, ignore_errors=True)

    def predict(self, features, all=False):

        predictions = list(self.model.predict(input_fn=self.dataset.input_predict_fn(features)))
        if all:
            return predictions
        if 'predictions' in predictions[0].keys():
            return predictions[0]['predictions'][0]
        return predictions[0]['classes'][0].decode("utf-8")

    def predict_test(self, test_file):
        self.test_file = test_file
        dict_results = {}
        # TODO maybe check if gpu is free

        predictions = list(self.model.predict(input_fn=self._test_input_fn))
        if 'predictions' in predictions[0].keys():
            preds = [x['predictions'][0] for x in predictions]
            dict_results['preds'] = preds
            return dict_results
        dict_results['preds'] = [x['classes'][0].decode("utf-8") for x in predictions]
        dict_results['logits'] = [x['logits'] for x in predictions]
        dict_results['scores'] = [x['probabilities'] for x in predictions]
        return dict_results

    def run(self):
        try:
            tf.estimator.train_and_evaluate(self.model, self.train_spec, self.eval_spec)
            self.email = self.params['email']
            server_info = {"login": "tf3deep",
                           "password": "tf3Deep123",
                           "email_address": "tf3deep@gmail.com"}

            send_email({"email_address": self.email}, server_info)
        except ValueError as e:
            tf.logging.error(e)

    def _create_explainer(self):
        return TabularExplainer(self.dataset) if isinstance(self.dataset, Tabular) else ImageExplainer(self.dataset)

    def explain(self, **params):
        explainer = self._create_explainer()
        # TODO explain on cpu, maybe check if gpu is free

        return explainer.explain_instance(self.model, **params)


class Estimator(AbstractEstimator):

    def __init__(self, params):
        super().__init__(params)

    def _create_model(self):
        self.label_unique_values = self.dataset.get_target_labels()
        self.params['n_classes'] = len(self.label_unique_values) if self.label_unique_values is not None else 0
        self.params['label_vocabulary'] = self.label_unique_values
        super()._create_model()


class MultOutEstimator(AbstractEstimator):

    def __init__(self, params):
        super().__init__(params)

    def predict(self, features, all=False):
        predictions = list(self.model.predict(input_fn=self.dataset.input_predict_fn(features)))

        if all:
            return predictions
        return predictions[0]['predictions']

    def predict_test(self, test_file):
        self.test_file = test_file
        dict_results = {}
        predictions = list(self.model.predict(input_fn=self._test_input_fn))
        dict_results['preds'] = [x['predictions'] for x in predictions]
        return dict_results

    def _create_model(self):
        self.params['label_dimension'] = len(self.dataset.get_targets())
        super()._create_model()
