from config import config_reader
import os


def get_hidden_layers(INPUT_DIM, OUTUPUT_DIM, num_samples, alpha=2):
    size = num_samples / (alpha * (INPUT_DIM + OUTUPUT_DIM))
    return str(int(round(size)))


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
