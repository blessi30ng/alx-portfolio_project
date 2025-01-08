from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    option_1 = db.Column(db.String(100), nullable=False)
    option_2 = db.Column(db.String(100), nullable=False)
    option_3 = db.Column(db.String(100), nullable=False)
    option_4 = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    