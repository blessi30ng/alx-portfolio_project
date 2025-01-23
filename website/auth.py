from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            if email is not None and password is not None:
                user = User.query.filter_by(email=email).first()
                if user:
                    if check_password_hash(user.password, password):
                        flash('Logged in successfully!', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('views.home'))
                    else:
                        flash('Password is incorrect, try again.', category='error')
                else:
                    flash('Email does not exist.', category='error')
    except SQLAlchemyError as e:
        flash(f'A database error occurred: {str(e)}', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    for _ in range(1):
        logout_user()
    flash("You have been logged out.", category='info')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user_exist = User.query.filter_by(email=email).first()  
        user = user_exist
        passwords_match = password1 == password2 

        if user is not None:
            flash('Email already exists.', category='error')
        elif len(email) < 5:
            flash('Email must be greater than 5 characters.', category='error')
        elif len(first_name) < 3:
            flash('First name must be greater than 2 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
            flash('Please ensure both passwords are identical.', category='info')
            flash('Password confirmation failed.', category='warning')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            new_user_details = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            
            print(new_user_details)

            db.session.add(new_user_details)
            db.session.commit()
            login_user(new_user_details, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)