from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(4, 100)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=100)])
    remember = BooleanField('Remember me')
    submit = SubmitField("Submit")
