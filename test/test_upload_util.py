from utils import upload_util
import os
import shutil
import pytest
from forms.upload_form import UploadForm, UploadNewForm

@pytest.fixture
def form():
    return UploadForm()


def test_generate_dataset_name():
    USER_ROOT = 'data_test'
    username = 'user'
    dataset_name = 'iris'
    os.makedirs(os.path.join(USER_ROOT, username, dataset_name))
    new_dataset_name = upload_util.generate_dataset_name(USER_ROOT, username, dataset_name)
    assert new_dataset_name == 'iris_1'
    shutil.rmtree(os.path.join(USER_ROOT, username, dataset_name))

