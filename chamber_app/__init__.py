# chamber_app/__init__.py

from flask import Flask, request, redirect, url_for
from flask_login import current_user
from .extensions import db, migrate, login_manager  # Import login_manager
from .filters import format_date
from config import Config
from .error_handlers import register_error_handlers
from .modules import register_blueprints
from .models.users import User


def create_app(config=Config):  # You can set a default config here
    app = Flask(__name__)

    app.config.from_object(config)
    app.jinja_env.filters['format_date'] = format_date

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)  # Initialize the login manager here

    @login_manager.user_loader
    def load_user(user_id):
        # Function to load a user by ID
        return User.query.get(int(user_id))

    @app.before_request
    def require_login():
        # Check if the request is for a static file or the login page
        if not current_user.is_authenticated and request.endpoint not in ['users.login', 'static']:
            return redirect(url_for('users.login'))

    with app.app_context():
        # Import models here to avoid circular imports
        from chamber_app.models import structure, library, ensemble
        register_error_handlers(app)
        register_blueprints(app)

    return app
