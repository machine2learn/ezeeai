from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(4, 16)])
    email = StringField("Email", validators=[InputRequired(), Email(message="invalid email"), Length(max=50)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=80)])
    password2 = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')
    submit = SubmitField("Submit")
