
import os
import socket
from utils import sys_ops
from dfweb import APP_ROOT
paths = ['a.ini', 'a2.ini']
export_dir = 'test_recursive/test'


def test_mkdir_recurstive():
    path = os.path.join(export_dir, paths[1])
    sys_ops.mkdir_recursive(path)
    assert os.path.exists(path) == True



def test_delete_recursive():
    sys_ops.delete_recursive(paths, export_dir)
    assert os.path.exists(os.path.join(export_dir, paths[0])) == False
    assert os.path.exists(os.path.join(export_dir, paths[1])) == False


def test_copyfile():
    filename = 'test_recursive/default_config.ini'
    destiny = 'test_recursive/default.ini'
    sys_ops.copyfile(filename, destiny)
    assert os.path.isfile(destiny) == True
    os.remove(destiny)


def test_not_existing_copyfile():
    filename = 'maindfasdfas.py'
    dest = 'test_recursive/default2.ini'
    sys_ops.copyfile(filename, dest)
    assert os.path.isfile(dest) == False


def test_find_free_port():
    port = sys_ops.find_free_port()
    p = int(port)
    assert isinstance(port, str)
    assert isinstance(p, int)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(("127.0.0.1", p))

    s.close()



def test_abs_path_of():
    path = 'data_test'
    assert sys_ops.abs_path_of(path) == APP_ROOT + '/utils/data_test'
