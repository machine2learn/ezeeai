from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import SubmitField, SelectField, FormField, SelectMultipleField, BooleanField, TextAreaField
from flask_uploads import UploadSet, DATA
from wtforms import StringField
from wtforms.widgets import HTMLString, html_params, TextArea
from wtforms.validators import InputRequired


class FileInputWithAccept:
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        return HTMLString(
            '<input %s>' % html_params(label=field.label, name=field.name, type='file', accept='text/csv', **kwargs))


class FileFieldWithAccept(StringField):
    widget = FileInputWithAccept()


dataset = UploadSet(extensions=DATA)


class NewFileForm(FlaskForm):
    train_file = FileFieldWithAccept(label='Train dataset in CSV format',
                                     validators=[FileAllowed(['csv'], message="Please enter csv file.")])

    test_file = FileFieldWithAccept(label='Validation dataset in CSV format (optional)',
                                    validators=[FileAllowed(['csv'], message="Please enter csv file.")],
                                    description='VALIDATION DATASET FILE: if not chosen, you can create the validation'
                                                'set from the train set in the next step.', )


class ExisitingDatasetForm(FlaskForm):
    train_file_exist = SelectField(u'Train dataset')


class IsExisiting(FlaskForm):
    is_existing = SelectField('Select an option to upload data: ',
                              choices=[('new_files', 'New files'),
                                       ('generate_data', 'Generate data')
                                       ])


class GenerateDataSet(FlaskForm):
    dataset_name = StringField("Dataset name")
    example_type = SelectField('Select an option to generate an example script : ',
                               choices=[('regression', 'Regression'),
                                        ('cluster', 'Classifier - Cluster'),
                                        ('decision_tree', 'Classifier - Decision Tree')
                                        ])
    script = TextAreaField("Script", render_kw={"rows": 25, "cols": 10})


class UploadForm(FlaskForm):
    options = FormField(IsExisiting)
    new_files = FormField(NewFileForm)
    generate_dataset = FormField(GenerateDataSet)
    submit = SubmitField("Submit")


class UploadNewForm(FlaskForm):
    new_files = FormField(NewFileForm)
    submit = SubmitField("Submit")
