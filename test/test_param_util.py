from utils import param_utils, preprocessing
from forms.parameters_form import GeneralClassifierForm, GeneralRegressorForm
import pandas as pd
import pytest

file = 'data_test/iris.csv'
config_file = 'data_test/iris_config.ini'
df = pd.read_csv('data_test/iris.csv')
categories = ['numerical', 'numerical', 'numerical', 'numerical', 'categorical']
unique_values = [-1, -1, -1, -1, 3]
default_list = {'sepal_length': 5.8, 'sepal_width': 3.0, 'petal_length': 4.35, 'petal_width': 1.3,
                'class': 'Iris-setosa'}
frequent_values2frequency = {'sepal_length': (5.0, 10), 'sepal_width': (3.0, 26), 'petal_length': (1.5, 14),
                             'petal_width': (0.2, 28), 'class': ('Iris-setosa', 50)}
SAMPLE_DATA_SIZE = 5
data = preprocessing.insert_data(df, categories, unique_values, default_list, frequent_values2frequency,
                                 SAMPLE_DATA_SIZE)
data.Category = categories
target = 'class'
train_file = 'data_test/iris.csv'


# @pytest.mark.parametrize("target_type, expect", [
#     ('categorical', GeneralClassifierForm),
#     ('numerical', GeneralRegressorForm)
# ])
# def test_define_param_form(target_type, expect):
#     form = param_utils.define_param_form(target_type)
#     assert isinstance(form, expect)

# def test_get_number_inputs():
#     assert param_utils.get_number_inputs(categories) == 4


@pytest.mark.parametrize("target, expect", [
    ('class', 5),
    ('petal_width', 11),
    (['petal_width','sepal_length'], 2),

])
# def test_get_number_outputs(target, expect):
#     assert param_utils.get_number_outputs(target, data) == expect
#

# def test_get_number_samples():
#     size = param_utils.get_number_samples(file)
#     assert isinstance(size, int)
#     assert size == 150
#

@pytest.mark.parametrize("INPUT_DIM, OUTUPUT_DIM, num_samples ,expect", [
    (4, 2, 50, '4'),
    (20, 1, 400, '10')
])
# def test_get_hidden_layers(INPUT_DIM, OUTUPUT_DIM, num_samples, expect):
#     size = param_utils.get_hidden_layers(INPUT_DIM, OUTUPUT_DIM, num_samples)
#     assert isinstance(size, str)
#     assert size == expect
#

@pytest.fixture
def form():
    return GeneralClassifierForm()

#
# def test_set_form():
#     param_utils.set_form(form(), config_file, 2)
