from chamber_app.extensions import db
from sqlalchemy.orm import relationship
from datetime import datetime


# Ensemble model with teacher relationship
class Ensemble(db.Model):
    __tablename__ = 'ensembles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    composition_id = db.Column(db.Integer, db.ForeignKey('compositions.id'))

    # Relationship to Composition
    composition = relationship('chamber_app.models.library.Composition', backref='ensembles', lazy=True)

    # One-to-many relationship to EnsembleTeacher
    teacher_assignments = relationship("chamber_app.models.structure.TeacherAssignment", back_populates="ensemble")
    assignments = relationship("EnsembleAssignment", back_populates="ensemble")
    # Relationship to Students
    ensemble_players = relationship(
        'EnsemblePlayer',
        back_populates='ensemble',
    )

    hour_donation = db.Column(db.Integer, default=2)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    ended = db.Column(db.DateTime)

    @property
    def student_completeness(self):
        players_in_ensemble = len(self.ensemble_players)
        students_assigned = self.count_assigned_students
        if players_in_ensemble == 0:
            return "No players required"
        return (students_assigned / players_in_ensemble) * 100

    @property
    def no_assigned_student(self):
        is_this_true = True
        for player in self.ensemble_players:
            if player.student_id:
                is_this_true = False
        return is_this_true

    @property
    def count_assigned_students(self):
        assigned_students = []
        for player in self.ensemble_players:
            if player.active_student_assignment:
                assigned_students.append(player.active_student_assignment)
        return len(assigned_students)

    @property
    def count_ensemble_players(self):
        return len(self.ensemble_players)

    @property
    def missing_instruments(self):
        required_instruments = set()
        assigned_instruments = set()

        # Gather required instruments from the composition
        for player in self.composition.players:
            for instrument in player.instruments:
                required_instruments.add(instrument.name)

        # Gather assigned instruments from the ensemble players
        for ensemble_player in self.ensemble_players:
            if ensemble_player.student_id:
                assigned_instruments.add(ensemble_player.student.instrument.name)

        # Determine missing instruments
        missing = required_instruments - assigned_instruments

        return list(missing)  # Return as a list for easier usage

    @property
    def instrumentation_text(self):
        """Returns a dictionary where the key is the Instrument object, sorted by 'order',
        and the value is a list of all players associated with that instrument."""
        instrument_player_dict = {}

        # Group players by instruments
        for player in self.ensemble_players:
            instrument = player.instrument  # Get the instrument for the player
            if instrument not in instrument_player_dict:
                instrument_player_dict[instrument] = []  # Initialize list for this instrument
            instrument_player_dict[instrument].append(player)  # Add player to the instrument's list

        # Sort the dictionary by the 'order' attribute of Instrument
        sorted_instrument_player_dict = dict(
            sorted(instrument_player_dict.items(), key=lambda item: item[0].order)
        )
        instrumentation_text = ""
        dict_length = len(sorted_instrument_player_dict)

        for index, (key, value) in enumerate(sorted_instrument_player_dict.items()):
            if len(value) == 1:
                if index == dict_length - 1:  # Last iteration
                    instrumentation_text += f"{key.name}"
                else:
                    instrumentation_text += f"{key.name}, "
            else:
                if index == dict_length - 1:  # Last iteration
                    instrumentation_text += f"{len(value)} {key.name}"
                else:
                    instrumentation_text += f"{len(value)} {key.name}, "

        return instrumentation_text

    @property
    def active_ensemble_assignments(self):
        return [assignment for assignment in self.assignments if assignment.ended is None]

    @property
    def active_student_assignments(self):
        active_students = []
        for player in self.ensemble_players:
            if player.active_student:
                active_students.append(player.active_student)

        # Sort the active students by the order of their instrument
        return sorted(active_students, key=lambda student: student.instrument.order)

    @property
    def active_teachers(self):
        active_teachers = []
        for a in self.teacher_assignments:
            if not a.ended:
                active_teachers.append(a.teacher)
        return active_teachers

    @property
    def active_teacher_assignments(self):
        active_teacher_assignments = []
        for a in self.teacher_assignments:
            if not a.ended:
                active_teacher_assignments.append(a)
        return active_teacher_assignments

    @property
    def remaining_hour_donation(self):
        total_donation = self.hour_donation
        assigned_donation = sum(a.hour_donation for a in self.active_teacher_assignments)
        remaining_donation = total_donation - assigned_donation
        return remaining_donation


class EnsembleAssignment(db.Model):
    __tablename__ = "ensemble_assignments"

    id = db.Column(db.Integer, primary_key=True)

    ensemble_id = db.Column(db.Integer, db.ForeignKey('ensembles.id'), nullable=False)
    composition_id = db.Column(db.Integer, db.ForeignKey('compositions.id'), nullable=False)

    # Relationships
    ensemble = relationship('Ensemble', back_populates='assignments')
    composition = relationship('Composition', back_populates='ensemble_assignments')

    created = db.Column(db.DateTime, default=datetime.utcnow)
    ended = db.Column(db.DateTime)


# Table to link students with ensembles and their instruments
class EnsemblePlayer(db.Model):
    __tablename__ = 'ensemble_players'

    id = db.Column(db.Integer, primary_key=True)
    ensemble_id = db.Column(db.Integer, db.ForeignKey('ensembles.id'), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'))

    # Relationships
    ensemble = db.relationship('Ensemble', back_populates='ensemble_players')
    student_assignments = db.relationship('StudentAssignment', back_populates='ensemble_player', lazy=True)
    instrument = db.relationship('Instrument', backref='ensemble_players', lazy=True)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    ended = db.Column(db.DateTime)

    @property
    def active_student_assignment(self):
        # Return the active assignment where 'ended_on' is None
        return next((assignment for assignment in self.student_assignments if assignment.ended is None), None)

    @property
    def active_student(self):
        # Return the student linked to the active assignment
        active_assignment = self.active_student_assignment
        return active_assignment.student if active_assignment else None
