from flask import Flask
import importlib
from .extensions import db, migrate
from .filters import format_date
from config import Config
import os
from .error_handlers import register_error_handlers
from .modules import register_blueprints


def create_app(config):
    app = Flask(__name__)

    app.config.from_object(config)
    app.jinja_env.filters['format_date'] = format_date

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import models here
        from chamber_app.models import structure, library, ensemble
        register_blueprints(app)

    return app
