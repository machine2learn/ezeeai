import random
import string
from datetime import datetime
from secrets import token_hex
from werkzeug.security import check_password_hash, generate_password_hash

from ..database.db import db
from ..database.user import User
from ..database.usersession import UserSession
from .sys_ops import create_user_path

EXPIRE_TIME = 60 * 60 * 24  # one day


def randomStringwithDigit(stringLength=32):
    """Generate a random string of letters, digits and special characters """
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength))


def get_db_user(username):
    return db.session.query(User.id).filter_by(username=username).scalar()


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_email_by_username(username):
    user = get_user_by_username(username)
    return user.email


def checklogin(form, login_user, session, sess, user_root, local_sess, appConfig):
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
        sess.add_user((session['user'], session['_id']))
        create_user_path(user_root, user.username, local_sess, session, appConfig)
        check_user_has_token(username)
        return True
    return False


def sign_up(form):
    hashed_passwd = generate_password_hash(form.password.data, method='sha256')
    token = randomStringwithDigit()
    if db.session.query(User.id).filter_by(username=form.username.data).scalar() is not None:
        return False
    new_user = User(username=form.username.data, email=form.email.data, password=hashed_passwd, token=token)
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


# USER SESSION

def get_usersession_by_username(username):
    return UserSession.query.filter_by(username=username).first()


def check_user_has_token(username):
    if db.session.query(UserSession.id).filter_by(username=username).scalar() is None:
        create_user_session(username)
    else:
        timestamp = db.session.query(UserSession.timestamp).filter_by(username=username).scalar()
        if (datetime.now() - timestamp).total_seconds() > EXPIRE_TIME or timestamp is None:
            # TOKEN EXPIRED
            token = randomStringwithDigit(32)
            update_token(username, token)
            update_timestamp(username)


def create_user_session(username):
    token = randomStringwithDigit(32)
    new_usersession = UserSession(username=username, token=token, timestamp=datetime.now())
    db.session.add(new_usersession)
    db.session.commit()
    return True


def update_token(username, token):
    user = get_usersession_by_username(username)
    user.token = token
    db.session.commit()


def update_timestamp(username):
    user = get_usersession_by_username(username)
    user.timestamp = datetime.now()
    db.session.commit()


def get_token_user(username):
    check_user_has_token(username)
    token = db.session.query(UserSession.token).filter_by(username=username).scalar()
    return token
