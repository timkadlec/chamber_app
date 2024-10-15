from chamber_app.extensions import db

# Import your models here
from .structure import Student, Teacher, Department
from .library import Composer, Composition, Player, Instrument
from .ensemble import Ensemble, EnsemblePlayer

# Optional: Expose your models for easier access
__all__ = [
    'db',
    'Student',
    'Composer',
    'Composition',
    'Player',
    'Instrument',
    'Teacher',
    'Department',
    'Ensemble',
    'EnsemblePlayer'
]
