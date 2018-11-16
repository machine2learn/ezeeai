import os
import tempfile

import pytest
from flask_login import LoginManager, login_user, login_required, logout_user
from utils import db_ops
from session import Session
from user import User
from flask import session, Flask
import sqlalchemy
from database.db import db
from flask_login import UserMixin
from user import User
from werkzeug.security import generate_password_hash
from dfweb import app
from database.db import db


# def test_add_user_db():
#     user = User()
#     db.session.add(user)
#     db.session.commit()
#     # this works
#     assert user in db.session
#     # this raises an AssertionError



def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    session.setdefault('test')
    # db.init_app(app)
    # app.run()
    return app


@pytest.fixture
def user():
    return User()

# def test_get_db_user(user: user()):
#     with create_app().app_context():
#         new_user = db_ops.get_db_user(user.username)

# def test_def_get_user_by_username():
#     with create_app().app_context():
#         username = 'test'
#         my_user= db_ops.get_user_by_username(username)


# def test_user():
#
#     hashed_passwd = generate_password_hash(password, method='sha256')
#     with create_app().app_context():
#         new_user = User(username=username, email=email, password=hashed_passwd)
#         db.session.add(new_user)
#         try:
#             db.session.commit()
#         except sqlalchemy.exc.IntegrityError:
#             db.session.rollback()

#
# def test_checklogin():
#     username = 'test'
#     password = 'test12345'
#     remember = False
#
#     db_ops.checklogin(username, password, remember, login_user, session, sess)
#
#     new_user = db.session.query(User.id).filter_by(username=_username).scalar()
#     if new_user is None:
#         return False
#     user = User.query.filter_by(username=_username).first()
#     if check_password_hash(user.password, _password):
#         login_user(user, remember=_remember)
#         session['user'] = user.username
#         sess.add_user(user.username)
#         if not os.path.exists(os.path.join('user_data/', user.username)):
#             os.mkdir(os.path.join('user_data/', user.username))
#         return True
#     return False
