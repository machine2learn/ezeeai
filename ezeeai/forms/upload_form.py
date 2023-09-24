from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import SubmitField, SelectField, FormField, SelectMultipleField, BooleanField, TextAreaField
from flask_uploads import UploadSet, DATA
from wtforms import StringField
from wtforms.widgets import html_params, TextArea
from markupsafe import Markup
from wtforms.validators import InputRequired


class FileInputWithAccept:
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        return Markup(
            '<input %s>' % html_params(label="CVS", name=field.name, type='file', accept='text/csv', **kwargs))


class FileFieldWithAccept(StringField):
    widget = FileInputWithAccept()


class ZipFileInputWithAccept:
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        return Markup(
            '<input %s>' % html_params(label="ZIP", name=field.name, type='file', accept='.zip', **kwargs))


class ZipFileFieldWithAccept(StringField):
    widget = ZipFileInputWithAccept()


class NumpyFileInputWithAccept:
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        return Markup(
            '<input %s>' % html_params(label="NPZ", name=field.name, type='file', accept='.npz', **kwargs))


class NumpyFileFieldWithAccept(StringField):
    widget = NumpyFileInputWithAccept()


dataset = UploadSet(extensions=DATA)


class NewTabularFileForm(FlaskForm):
    train_file = FileFieldWithAccept(label='Train dataset in CSV format',
                                     validators=[FileAllowed(['csv'], message="Please enter csv file.")])

    test_file = FileFieldWithAccept(label='Test dataset in CSV format (optional)',
                                    validators=[FileAllowed(['csv'], message="Please enter csv file.")],
                                    description='TEST DATASET FILE: if not chosen, you can create the test'
                                                'set from the train set in the next step.', )


class NewImageFileForm(FlaskForm):
    selector = SelectField("Select format option",
                           choices=[('option1', 'Folder per class'),
                                    ('option2', 'All same folder with label file'),
                                    ('option3', 'Numpy file')],
                           default='option1',
                           description="")


class NewImageOption1(FlaskForm):
    file = ZipFileFieldWithAccept(label='Zip images',
                                  validators=[FileAllowed(['zip'], message="Please enter zip .")])


class NewImageOption2(FlaskForm):
    file = ZipFileFieldWithAccept(label='Zip images',
                                  validators=[FileAllowed(['zip'], message="Please enter zip .")])


class NewImageOption3(FlaskForm):
    file = NumpyFileFieldWithAccept(label='Numpy file',
                                    validators=[FileAllowed(['npy', 'npz'], message="Please enter numpy file.")])


class GenerateDataSet(FlaskForm):
    dataset_name = StringField("Dataset name")
    example_type = SelectField('Select an option to generate an example script',
                               choices=[('regression', 'Regression'),
                                        ('cluster', 'Classifier - Cluster'),
                                        ('decision_tree', 'Classifier - Decision Tree')
                                        ])
    script = TextAreaField("Script", render_kw={"rows": 0, "cols": 10})


class UploadImageForm(FlaskForm):
    selector = FormField(NewImageFileForm)
    option1 = FormField(NewImageOption1)
    option2 = FormField(NewImageOption2)
    option3 = FormField(NewImageOption3)
    submit = SubmitField("Submit")
