from chamber_app.extensions import db
from sqlalchemy.orm import relationship

# Association table for the many-to-many relationship between ensembles and compositions
ensemble_composition = db.Table('ensemble_composition',
                                db.Column('ensemble_id', db.Integer, db.ForeignKey('ensembles.id'), primary_key=True),
                                db.Column('composition_id', db.Integer, db.ForeignKey('compositions.id'),
                                          primary_key=True),
                                db.Column('status', db.String(50), nullable=False, default="studying")
                                # Track work status (e.g., studying, completed)
                                )


# Ensemble model with teacher relationship
class Ensemble(db.Model):
    __tablename__ = 'ensembles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    composition_id = db.Column(db.Integer, db.ForeignKey('compositions.id'))

    # Relationship to Composition
    composition = relationship('Composition', backref='ensembles', lazy=True)

    # One-to-many relationship to EnsembleTeacher
    ensemble_teachers = relationship('EnsembleTeacher', back_populates='ensemble')

    # Relationship to Students
    ensemble_players = relationship('EnsemblePlayer', back_populates='ensemble')

    @property
    def player_completeness(self):
        total_players = self.composition.player_count
        assigned_players = self.count_assigned_students
        if total_players == 0:
            return "No players required"
        return (assigned_players / total_players) * 100

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
            if player.student_id:
                assigned_students.append(assigned_students)
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
    def student_members(self):
        students = []
        for player in self.ensemble_players:
            if player.student_id:
                students.append(player.student)
        return students


# Table to link students with ensembles and their instruments
class EnsemblePlayer(db.Model):
    __tablename__ = 'ensemble_players'

    id = db.Column(db.Integer, primary_key=True)
    ensemble_id = db.Column(db.Integer, db.ForeignKey('ensembles.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'))

    # Relationships
    ensemble = relationship('Ensemble', back_populates='ensemble_players')
    student = relationship('Student', backref='ensemble_assignments', lazy=True)
    instrument = relationship('Instrument', backref='ensemble_players', lazy=True)


class EnsembleTeacher(db.Model):
    __tablename__ = 'ensemble_teachers'

    id = db.Column(db.Integer, primary_key=True)
    ensemble_id = db.Column(db.Integer, db.ForeignKey('ensembles.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))

    # Any additional data about the relationship can be added here, such as role, assignment date, etc.
    role = db.Column(db.String(128))  # Optional field for teacher's role in the ensemble
    assignment_date = db.Column(db.Date)  # Optional field for when the teacher was assigned to the ensemble

    # Relationship to Ensemble and Teacher
    ensemble = relationship('Ensemble', back_populates='ensemble_teachers')
    teacher = relationship('Teacher', back_populates='ensemble_teachers')
