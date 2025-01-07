from flask import Blueprint
from chamber_app.models.module_base import ModuleBase

dashboard_bp = Blueprint('dashboard', __name__, template_folder="templates")


class DashboardModule(ModuleBase):
    def __init__(self):
        super().__init__(name="dashboard", description="Dashboard of the app.")


from . import routes
