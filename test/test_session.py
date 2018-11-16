from flask import Flask
from session import Session
from user import User
import pytest
from flask import session, redirect, url_for


def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    return app


@pytest.fixture
def user():
    return User()


@pytest.fixture
def session():
    return Session(create_app())


def test_add_user(user):
    session().add_user(user)
#
# def test_reset_user():
#     with session()._app.app_context():
#         session().reset_user()
#
#
# def test_get_session(app : create_app()):
#     with app.app_context():
#         user_id = user().id
#         session(app).get_session(user_id)

# def test_set():
#     key = 'key'
#     value = 'value'
#     session().set(key, value)
#     assert  session().get(key) == value
#
# def test_update_split(session: session()):
#     session.update_split('data_test/iris.csv', 'data_test/iris.csv')
