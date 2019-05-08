from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .db import db
from .user import User
from flask_login import UserMixin


class UserSession(UserMixin, db.Model):
    __tablename__ = 'usersession'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), ForeignKey(User.username), unique=True)
    token = db.Column(db.String(32), unique=False)
    timestamp = db.Column(db.TIMESTAMP, unique=False)

    user = relationship('User', foreign_keys='UserSession.username')