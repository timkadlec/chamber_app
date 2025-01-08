from flask import render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required
from chamber_app.forms import RegistrationForm, LoginForm
from chamber_app.models.users import User
from chamber_app.extensions import db
from . import auth_bp
from ...decorators import is_admin
import string, random


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a user object with the username, first name, last name, and email
        new_user = User(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data
        )
        new_user.set_password(form.password.data)  # Hash the password before storing
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if the input is an email or username
        user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.username.data)  # Assuming the field in the form is still called 'username'
        ).first()

        # Use the check_password method to validate the password
        if user and user.check_password(form.password.data):
            session['logged_in'] = True
            session['user_id'] = user.id
            login_user(user)
            return redirect(url_for('dashboard.home_view'))  # Redirect to a main page
        else:
            flash('Login failed. Check your username or email and password.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    session['logged_in'] = False
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/change_password')
@login_required
def change_password():

    logout_user()
    return redirect(url_for('auth.login'))