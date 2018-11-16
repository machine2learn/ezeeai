from forms.parameters_form import GeneralParamForm
import pandas as pd
from config import config_reader
import os


def get_number_inputs(categories):
    return len([categories[i] for i in range(len(categories)) if categories[i] != 'none']) - 1


def get_number_outputs(targets, data):
    if len(targets) > 1:
        return len(targets)
    target_type = data.Category[targets[0]]
    return 1 if target_type == 'numerical' else data['#Unique Values'][targets[0]]


def get_number_samples(file):
    return len(pd.read_csv(file).index)


def set_form(form, CONFIG_FILE):
    if os.path.isfile(CONFIG_FILE):
        reader = config_reader.read_config(CONFIG_FILE)
        if 'EXPERIMENT' in reader.keys():
            form.experiment.form.keep_checkpoint_max.default = reader['EXPERIMENT']['keep_checkpoint_max']
            form.experiment.form.save_checkpoints_steps.default = reader['EXPERIMENT']['save_checkpoints_steps']
            form.experiment.form.save_summary_steps.default = reader['EXPERIMENT']['save_summary_steps']
            form.experiment.form.throttle.default = reader['EXPERIMENT']['throttle']
            form.experiment.form.validation_batch_size.default = reader['EXPERIMENT']['validation_batch_size']
        if 'TRAINING' in reader.keys():
            form.training.form.num_epochs.default = reader['TRAINING']['num_epochs']
            form.training.form.batch_size.default = reader['TRAINING']['batch_size']
            form.training.form.optimizer.default = reader['TRAINING']['optimizer']
            form.training.form.learning_rate.default = reader['TRAINING']['learning_rate']
    form.experiment.form.process()
    form.training.form.process()


