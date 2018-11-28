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


class NewTabularFileForm(FlaskForm):
    train_file = FileFieldWithAccept(label='Train dataset in CSV format',
                                     validators=[FileAllowed(['csv'], message="Please enter csv file.")])

    test_file = FileFieldWithAccept(label='Test dataset in CSV format (optional)',
                                    validators=[FileAllowed(['csv'], message="Please enter csv file.")],
                                    description='TEST DATASET FILE: if not chosen, you can create the test'
                                                'set from the train set in the next step.', )


class GenerateDataSet(FlaskForm):
    dataset_name = StringField("Dataset name")
    example_type = SelectField('Select an option to generate an example script : ',
                               choices=[('regression', 'Regression'),
                                        ('cluster', 'Classifier - Cluster'),
                                        ('decision_tree', 'Classifier - Decision Tree')
                                        ])
    script = TextAreaField("Script", render_kw={"rows": 25, "cols": 10})


class UploadForm(FlaskForm):
    new_tabular_files = FormField(NewTabularFileForm)
    generate_dataset = FormField(GenerateDataSet)
    submit = SubmitField("Submit")
