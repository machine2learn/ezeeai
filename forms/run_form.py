from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField
from wtforms.widgets import HTMLString, html_params, Input


class RunForm(FlaskForm):
    submit = SubmitField("Run")
