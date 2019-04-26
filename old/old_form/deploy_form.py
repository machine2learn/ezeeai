from flask_wtf import FlaskForm
from wtforms import SubmitField, TextField, FormField, FileField, IntegerField, FieldList, SelectField, FloatField, \
    BooleanField
from wtforms.validators import InputRequired, ValidationError, StopValidation, AnyOf, Regexp, NumberRange, Length

from wtforms import StringField


class DeploymentForm(FlaskForm):
    model_name = StringField("Model name", validators=[InputRequired(), Length(min=4, max=25)],
                             default="",
                             description="All checkpoints will be saved as different versions of this model.")
    gen_script = BooleanField("Generate deployment script", default=True,
                              description="Generate the bash script to deploy with docker and Tensorflow Serving.")
    submit = SubmitField("Export")
