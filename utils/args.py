import os
import pandas as pd


def assert_file(file):
    if not isinstance(file, str):
        raise TypeError(f'must be str, not {file.__class__}')
    if not os.path.isfile(file):
        raise FileNotFoundError(f'file not found: {file}')


def assert_folder(folder):
    if not isinstance(folder, str):
        raise TypeError(f'must be str, not {folder.__class__}')
    if not os.path.isdir(folder):
        raise FileNotFoundError(f'folder not found: {folder}')


def assert_type(type, arg):
    if not isinstance(arg, type):
        raise TypeError(f'must be {type.__name__}, not {arg.__class__}')

