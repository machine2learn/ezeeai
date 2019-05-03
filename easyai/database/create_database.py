from .user import User
from werkzeug.security import generate_password_hash
from ..dfweb import app

USERNAME = 'test'
PASSWORD = 'test_machine2learn'
EMAIL = 'test@test.com'


def create_all():  # TODO not used/not working
    from .db import db
    with app.app_context():
        db.init_app(app)
        db.create_all()
        db.session.commit()
        new_user = create_new_user(USERNAME, PASSWORD, EMAIL)
        db.session.add(new_user)
        db.session.commit()
    return True


def create_new_user(username, password, email):
    from .db import db
    with app.app_context():
        db.init_app(app)
        hashed_passwd = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_passwd)
        db.session.add(new_user)
        db.session.commit()
    return True


if __name__ == '__main__':
    create_all()
