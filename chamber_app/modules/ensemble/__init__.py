from flask import Blueprint

ensemble_bp = Blueprint('ensemble', __name__, template_folder="templates")

from . import routes
