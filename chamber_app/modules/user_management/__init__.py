from flask import Blueprint

user_management_bp = Blueprint('user_management', __name__, template_folder="templates")

from . import routes
