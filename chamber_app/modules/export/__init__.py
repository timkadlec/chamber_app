from flask import Blueprint

export_bp = Blueprint('export', __name__, template_folder="templates", static_folder='static')

from . import routes
