from ..database.db import db
from secrets import token_hex
from ..database.user import User
from werkzeug.security import check_password_hash, generate_password_hash
from .sys_ops import create_user_path


def get_db_user(username):
    return db.session.query(User.id).filter_by(username=username).scalar()


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_email_by_username(username):
    user = get_user_by_username(username)
    return user.email


def checklogin(form, login_user, session, sess, user_root):
    username = form.username.data
    password = form.password.data
    remember = form.remember.data
    new_user = get_db_user(username)
    if new_user is None:
        return False
    user = get_user_by_username(username)
    if check_password_hash(user.password, password):
        login_user(user, remember=remember)
        session['user'] = user.username
        session['token'] = token_hex(16)
        sess.add_user((session['user'], session['_id']))
        create_user_path(user_root, user.username)
        return True
    return False


def sign_up(form):
    hashed_passwd = generate_password_hash(form.password.data, method='sha256')
    if db.session.query(User.id).filter_by(username=form.username.data).scalar() is not None:
        return False
    new_user = User(username=form.username.data, email=form.email.data, password=hashed_passwd)
    db.session.add(new_user)
    db.session.commit()
    return True


def get_user_data(username, form):
    user = get_user_by_username(username)
    form.username.default = user.username
    form.email.default = user.email
    form.process()


def update_user(username, email):
    user = get_user_by_username(username)
    user.email = email
    db.session.commit()


def get_email(username):
    user = get_user_by_username(username)
    return user.email
