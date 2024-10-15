from flask import Blueprint

library_bp = Blueprint('library', __name__, template_folder="templates")

from . import routes
