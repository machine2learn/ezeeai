from flask_wtf import FlaskForm
from wtforms import SubmitField, TextField, FormField, FileField, IntegerField, FieldList, SelectField, FloatField, \
    BooleanField
from wtforms.validators import InputRequired, ValidationError, StopValidation, AnyOf, Regexp, NumberRange

#
# def validate_int(form, field):
#     try:
#         int(field.raw_data)
#         return True
#     except:
#         return False

class ExperimentForm(FlaskForm):
    keep_checkpoint_max = IntegerField("Maximum # of checkpoints", validators=[InputRequired()], default=5,
                                       description="MAXIMUN # OF CHECKPOINTS : The maximum number of recent checkpoint files to keep. As new files are created, older files are deleted. If None or 0, all checkpoint files are kept.")
    save_checkpoints_steps = IntegerField("Save checkpoints after", validators=[InputRequired()], default=50,
                                          description="SAVE CHECKPOINTS STEPS : The frequency, in number of global steps, that the global step/sec and the loss will be logged during training.")
    save_summary_steps = IntegerField("Save summary after", validators=[InputRequired()], default=5,
                                      description="SAVE SUMMARY AFTER: Save summaries every this many steps.")
    throttle = IntegerField("Evaluate after (s)", validators=[InputRequired()], default=1,
                            description="EVALUATE AFTER (S):  Do not re-evaluate unless the last evaluation was started at least this many seconds ago. Of course, evaluation does not occur if no new checkpoints are available, hence, this is the minimum.")


class TrainForm(FlaskForm):
    num_epochs = IntegerField("Number of epochs", validators=[InputRequired()], default=100,
                              description="NUMBER OF EPOCHS: Number of epochs to iterate over data.")
    batch_size = IntegerField("Batch size", validators=[InputRequired()], default=32,
                              description="BATCH SIZE: An integer indicating the desired batch size. Batch Normalization is a technique that normalizes layer inputs per mini-batch. It speed up training, allows for the usage of higher learner rates, and can act as a regularizer.")
    optimizer = SelectField("Optimizer",
                            choices=[('Adagrad', 'Adagrad'), ('Adam', 'Adam'), ('Ftrl', 'Ftrl'), ('RMSProp', 'RMSProp'),
                                     ('SGD', 'SGD')], default='Adam',
                            description="OPTIMIZER: Provides methods to compute gradients for a loss and apply gradients to variables."
                                        "The options to pass to optimizer parameter are: Adagrad, Adam, Ftrl, RMSProp, SGD. ")

    learning_rate = FloatField("Learning rate", validators=[InputRequired()], default=0.01,
                               description="LEARNING RATE: A constant at the beginning of your code right after the logging configuration.")


class GeneralParamForm(FlaskForm):
    experiment = FormField(ExperimentForm)
    training = FormField(TrainForm)
    submit = SubmitField("Submit")
