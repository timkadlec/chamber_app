from .dashboard import dashboard_bp  # Assuming 'dashboard.py' contains the blueprint
from .library import library_bp
from .settings import settings_bp
from .structure import structure_bp
from .ensemble import ensemble_bp


def register_blueprints(app):
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(library_bp, url_prefix="/library")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(structure_bp, url_prefix="/structure")
    app.register_blueprint(ensemble_bp, url_prefix="/ensembles")
