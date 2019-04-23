from flask_wtf import FlaskForm
from wtforms import SubmitField, FormField, IntegerField, SelectField, FloatField
from wtforms.validators import InputRequired

inputs = {
    'keep_checkpoint_max': {
        'label': "Maximum # of checkpoints",
        'description': "MAXIMUN # OF CHECKPOINTS : The maximum number of recent checkpoint files to keep. As new files are created, older files are deleted. If None or 0, all checkpoint files are kept."

    },
    'save_checkpoints_steps': {
        'label': "Save checkpoints after",
        'description': "SAVE CHECKPOINTS STEPS : The frequency, in number of global steps, that the global step/sec and the loss will be logged during training."
    },
    'save_summary_steps': {
        'label': "Save summary after",
        'description': "SAVE SUMMARY AFTER: Save summaries every this many steps."
    },
    'throttle': {
        'label': "Evaluate after (s)",
        'description': "EVALUATE AFTER (S):  Do not re-evaluate unless the last evaluation was started at least this many seconds ago. Of course, evaluation does not occur if no new checkpoints are available, hence, this is the minimum."

    },

    'num_epochs': {
        'label': "Number of epochs",
        'description': "NUMBER OF EPOCHS: Number of epochs to iterate over data."
    },

    'batch_size': {
        'label': "Batch size",
        'description': "BATCH SIZE: An integer indicating the desired batch size. Batch Normalization is a technique that normalizes layer inputs per mini-batch. It speed up training, allows for the usage of higher learner rates, and can act as a regularizer."
    },

    'optimizer': {
        'label': "Optimizer",
        'description': "OPTIMIZER: Provides methods to compute gradients for a loss and apply gradients to variables."
                       "The options to pass to optimizer parameter are: Adagrad, Adam, Ftrl, RMSProp, SGD. "
    },

    'learning_rate': {
        'label': "Learning rate",
        'description': "LEARNING RATE: A constant at the beginning of your code right after the logging configuration."
    }
}


class ExperimentForm(FlaskForm):
    keep_checkpoint_max = IntegerField(inputs['keep_checkpoint_max']['label'],
                                       validators=[InputRequired()],
                                       default=5,
                                       description=inputs['keep_checkpoint_max']['description'])

    save_checkpoints_steps = IntegerField(inputs['save_checkpoints_steps']['label'],
                                          validators=[InputRequired()],
                                          default=50,
                                          description=inputs['save_checkpoints_steps']['description'])

    save_summary_steps = IntegerField(inputs['save_summary_steps']['label'],
                                      validators=[InputRequired()],
                                      default=5,
                                      description=inputs['save_summary_steps']['description'])

    throttle = IntegerField(inputs['throttle']['label'],
                            validators=[InputRequired()],
                            default=1,
                            description=inputs['throttle']['description'])


class TrainForm(FlaskForm):
    num_epochs = IntegerField(inputs['num_epochs']['label'],
                              validators=[InputRequired()],
                              default=100,
                              description=inputs['num_epochs']['description'])

    batch_size = IntegerField(inputs['batch_size']['label'],
                              validators=[InputRequired()],
                              default=32,
                              description=inputs['batch_size']['description'])

    optimizer = SelectField(inputs['optimizer']['label'],
                            choices=[('Adagrad', 'Adagrad'), ('Adam', 'Adam'), ('Ftrl', 'Ftrl'),
                                     ('RMSProp', 'RMSProp'),
                                     ('SGD', 'SGD')], default='Adam',
                            description=inputs['optimizer']['description'])

    learning_rate = FloatField(inputs['learning_rate']['label'],
                               validators=[InputRequired()],
                               default=0.01,
                               description=inputs['learning_rate']['description'])


class GeneralParamForm(FlaskForm):
    experiment = FormField(ExperimentForm)
    training = FormField(TrainForm)
    submit = SubmitField("Submit")
