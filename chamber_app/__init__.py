from flask import Flask
import importlib
from .extensions import db, migrate
from .filters import format_date
from config import Config
import os
from .modules import dashboard_bp, library_bp, settings_bp, structure_bp, ensemble_bp

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
        
        app.register_blueprint(dashboard_bp, url_prefix="/")
        app.register_blueprint(library_bp, url_prefix="/library")
        app.register_blueprint(settings_bp, url_prefix="/settings")
        app.register_blueprint(structure_bp, url_prefix="/structure")
        app.register_blueprint(ensemble_bp, url_prefix="/ensembles")
        # Import routes to avoid circular imports
        # Ensure you define blueprints in their respective modules
        # from .modules.front_end import front_end_bp
        # app.register_blueprint(front_end_bp)

        # Optional: Create the database tables if they don't exist
        # db.create_all()

    return app
