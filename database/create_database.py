from user import User
from werkzeug.security import generate_password_hash
from dfweb import app

def create_all():
    from database.db import db
    with app.app_context():
        db.init_app(app)
        db.create_all()
        db.session.commit()
        hashed_passwd = generate_password_hash('test12345', method='sha256')
        new_user = User(username='test', email='test@test.com', password=hashed_passwd)
        db.session.add(new_user)
        db.session.commit()
    return True


def create_new_user(username, password, email):
    from database.db import db
    with app.app_context():
        db.init_app(app)
        hashed_passwd = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_passwd)
        db.session.add(new_user)
        db.session.commit()
    return True


#
# username = 'test2'
# password= 'test12345'
# email = 'test2@test.com'
# create_new_user(username, password, email)