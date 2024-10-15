from chamber_app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Integer, String

# Teacher model
class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)

# Department model
class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)

# StudyProgram model
class StudyProgram(db.Model):
    __tablename__ = 'study_programs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1), unique=True, nullable=False)  # 'B' or 'N'
    # Add a weight for program comparison (e.g., B=1, N=2)
    weight = db.Column(db.Integer)
    
    # Establish relationship to 'Year'
    years = relationship("Year", backref='study_program', lazy=True)

# Year model
class Year(db.Model):
    __tablename__ = 'years'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)  # 1, 2, 3 (or just 1, 2 for 'N')
    
    # Link each year to a StudyProgram
    study_program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'), nullable=False)

# Student model
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(256), nullable=False)
    osobni_cislo = db.Column(db.String(256), unique=True, nullable=False)
    
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    study_program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'))
    year_id = db.Column(db.Integer, db.ForeignKey('years.id'))

    # Relationships
    instrument = relationship("chamber_app.models.library.Instrument", backref='students', lazy=True)
    teacher = relationship("chamber_app.models.structure.Teacher", backref='students', lazy=True)
    department = relationship("chamber_app.models.structure.Department", backref='students', lazy=True)
    study_program = relationship("StudyProgram", backref='students', lazy=True)
    year = relationship("Year", backref='students', lazy=True)
