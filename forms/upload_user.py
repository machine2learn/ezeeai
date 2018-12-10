from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,  BooleanField
from wtforms.validators import InputRequired, Email, Length


class UploadUserForm(FlaskForm):
    username = StringField("Username")
    email = StringField("Email", validators=[InputRequired(), Email(message="invalid email"), Length(max=50)])
    send_mail = BooleanField("I do not want to receive mails")
    submit = SubmitField("Save")
