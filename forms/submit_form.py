from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField
from wtforms.widgets import HTMLString, html_params, Input, CheckboxInput


# class DisabledSubmitInput(Input):
#     input_type = 'submit'
#
#     def __call__(self, field, **kwargs):
#         kwargs.setdefault('value', field.label.text)
#         return super(DisabledSubmitInput, self).__call__(field, disabled=True, **kwargs)
#
#
# class DisabledSubmit(BooleanField):
#     widget = DisabledSubmitInput()

class Submit(FlaskForm):
    # submit = DisabledSubmit("Next")
    submit = SubmitField("Next")
