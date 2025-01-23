from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "quizhub.db"

class Config:
    """Configuration settings for the Flask app"""
    SECRET_KEY = os.environ.get('SECRET_KEY', None)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DB_NAME}')

    if SECRET_KEY is None:
        raise ValueError("No SECRET_KEY set for Flask application")

    if SQLALCHEMY_DATABASE_URI is None:
        raise ValueError("No DATABASE_URL set for Flask application")
    
def create_app():
    """zz
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


