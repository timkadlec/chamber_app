from flask import Blueprint

structure_bp = Blueprint('structure', __name__, template_folder="templates")

from . import routes
