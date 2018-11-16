from database.db import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(50), unique=False)
    password = db.Column(db.String(80))

