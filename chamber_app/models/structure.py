from chamber_app.extensions import db
from sqlalchemy.orm import relationship
from datetime import datetime


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)

    assignments = db.relationship('TeacherAssignment', back_populates='teacher')


class TeacherAssignment(db.Model):
    __tablename__ = "teacher_assignments"
    id = db.Column(db.Integer, primary_key=True)

    ensemble_id = db.Column(db.Integer, db.ForeignKey('ensembles.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)

    teacher = db.relationship('Teacher', back_populates='assignments')
    ensemble = db.relationship('chamber_app.models.ensemble.Ensemble', back_populates="teacher_assignments")

    started_on = db.Column(db.DateTime, default=datetime.utcnow)
    ended_on = db.Column(db.DateTime)


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)


# StudyProgram model
class StudyProgram(db.Model):
    __tablename__ = 'study_programs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1), unique=True, nullable=False)  # 'B' or 'N'
    weight = db.Column(db.Integer)  # Weight for program comparison


# ClassYear model
class ClassYear(db.Model):
    __tablename__ = 'class_years'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)  # 1, 2, 3 (or just 1, 2 for 'N')

    # Link each year to a StudyProgram
    study_program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'), nullable=False)

    # Use the class name 'StudyProgram' for the relationship
    study_program = db.relationship("StudyProgram", backref=db.backref('class_years', lazy=True))


class StudentStatus(db.Model):
    __tablename__ = 'student_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    shortcut = db.Column(db.String(50), nullable=True)


# Student model
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(256), nullable=False)
    osobni_cislo = db.Column(db.String(256), unique=True)
    guest = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    study_program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'))
    class_year_id = db.Column(db.Integer, db.ForeignKey('class_years.id'))
    student_status_id = db.Column(db.Integer, db.ForeignKey('student_status.id'))

    # Relationships
    assignments = db.relationship('StudentAssignment', back_populates='student')
    instrument = relationship("chamber_app.models.library.Instrument", backref='students', lazy=True)
    teacher = relationship("chamber_app.models.structure.Teacher", backref='students', lazy=True)
    department = relationship("chamber_app.models.structure.Department", backref='students', lazy=True)
    study_program = relationship("StudyProgram", backref='students', lazy=True)
    class_year = relationship("ClassYear", backref='students', lazy=True)
    student_status = relationship("StudentStatus", backref='students', lazy=True)


class StudentAssignment(db.Model):
    __tablename__ = "student_assignments"
    id = db.Column(db.Integer, primary_key=True)

    ensemble_id = db.Column(db.Integer, db.ForeignKey('ensembles.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    student = db.relationship('Student', back_populates='assignments')
    ensemble = db.relationship('chamber_app.models.ensemble.EnsemblePlayer', back_populates="student_assignments")

    started_on = db.Column(db.DateTime, default=datetime.utcnow)
    ended_on = db.Column(db.DateTime)
    deleted = db.Column(db.DateTime)


class Nationality(db.Model):
    __tablename__ = 'nationalities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)


class AcademicYear(db.Model):
    __tablename__ = "academic_years"
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Date)
    end = db.Column(db.Date)

    semesters = db.relationship("Semester", backref="academic_year")


class Semester(db.Model):
    __tablename__ = "semesters"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
