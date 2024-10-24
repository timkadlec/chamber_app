from chamber_app.extensions import db
from sqlalchemy.orm import relationship
from datetime import datetime
import math


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    import_name = db.Column(db.String(256), unique=True, nullable=False)
    employment_time = db.Column(db.Float)
    academic_position_id = db.Column(db.Integer, db.ForeignKey('academic_positions.id'))

    academic_position = db.relationship('AcademicPosition', backref='teachers')
    departments = db.relationship('TeacherDepartment', back_populates='teacher')
    class_assignments = db.relationship('TeacherClassAssignment', back_populates='teacher')
    chamber_assignments = db.relationship('TeacherChamberAssignment', back_populates='teacher')

    @property
    def full_name(self):
        if self.academic_position:
            return f"{self.academic_position.shortcut} {self.name}"
        else:
            return self.name

    @property
    def active_chamber_assignments(self):
        return [assignment for assignment in self.chamber_assignments if assignment.ended is None]

    @property
    def active_class_assignments(self):
        active_assignments = [assignment for assignment in self.class_assignments if assignment.ended is None]

        active_assignments_sorted = sorted(active_assignments, key=lambda a: a.student.last_name)

        return active_assignments_sorted

    @property
    def active_assignments_hours(self):
        active_hours = 0
        for a in self.active_chamber_assignments:
            active_hours += a.hour_donation
        for a in self.active_class_assignments:
            active_hours += a.hour_donation
        return math.ceil(active_hours)

    @property
    def required_hours(self):
        if self.employment_time is None:
            return "Bez úvazku nelze vypočítat"  # Return the message as a string
        full_time = self.academic_position.full_time
        required_time = self.employment_time * full_time
        return math.ceil(required_time)

    @property
    def remaining_hours(self):
        if self.employment_time is None:
            return "Bez úvazku nelze vypočítat"  # Return the message as a string
        active_assignments_hours = self.active_assignments_hours
        needed_hours = self.required_hours
        required_time = needed_hours - active_assignments_hours
        return math.ceil(required_time)

    @property
    def employment_time_fulfilment(self):
        if self.employment_time:  # Ensure required hours are greater than zero to avoid division by zero
            percentage = (int(self.active_assignments_hours) / int(self.required_hours)) * 100
            return round(percentage, 2)  # Round to two decimal places for better readability
        else:
            return 0  # If no required hours, return 0


class TeacherClassAssignment(db.Model):
    __tablename__ = "teacher_class_assignments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hour_donation = db.Column(db.Integer)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)

    teacher = db.relationship('Teacher', back_populates='class_assignments')
    student = db.relationship('Student', back_populates="class_assignments")

    created = db.Column(db.DateTime, default=datetime.utcnow)
    ended = db.Column(db.DateTime)


class TeacherChamberAssignment(db.Model):
    __tablename__ = "teacher_chamber_assignments"
    id = db.Column(db.Integer, primary_key=True)
    hour_donation = db.Column(db.Integer)

    ensemble_id = db.Column(db.Integer, db.ForeignKey('ensembles.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)

    teacher = db.relationship('Teacher', back_populates='chamber_assignments')
    ensemble = db.relationship('chamber_app.models.ensemble.Ensemble', back_populates="teacher_assignments")

    created = db.Column(db.DateTime, default=datetime.utcnow)
    ended = db.Column(db.DateTime)


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)

    teacher_departments = db.relationship('TeacherDepartment', back_populates='department')


class TeacherDepartment(db.Model):
    __tablename__ = 'teacher_departments'
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key relationships
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    # Optional fields, e.g., when the teacher was assigned to the department
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships back to the Teacher and Department
    teacher = db.relationship('Teacher', back_populates='departments')
    department = db.relationship('Department', back_populates='teacher_departments')


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
    chamber_assignments = db.relationship('StudentChamberAssignment', back_populates='student')
    class_assignments = db.relationship('TeacherClassAssignment', back_populates='student')
    instrument = relationship("chamber_app.models.library.Instrument", backref='students', lazy=True)
    teacher = relationship("chamber_app.models.structure.Teacher", backref='students', lazy=True)
    department = relationship("chamber_app.models.structure.Department", backref='students', lazy=True)
    study_program = relationship("StudyProgram", backref='students', lazy=True)
    class_year = relationship("ClassYear", backref='students', lazy=True)
    student_status = relationship("StudentStatus", backref='students', lazy=True)

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def active_assignments(self):
        return [assignment for assignment in self.assignments if assignment.ended is None]


class StudentChamberAssignment(db.Model):
    __tablename__ = "student_chamber_assignments"
    id = db.Column(db.Integer, primary_key=True)

    ensemble_player_id = db.Column(db.Integer, db.ForeignKey('ensemble_players.id'),
                                   nullable=False)  # Foreign key to EnsemblePlayer
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    # Relationships
    student = db.relationship('Student', back_populates='chamber_assignments')
    ensemble_player = db.relationship('EnsemblePlayer', back_populates='student_assignments')

    created = db.Column(db.DateTime, default=datetime.utcnow)
    ended = db.Column(db.DateTime)


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


class AcademicPosition(db.Model):
    __tablename__ = 'academic_positions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    shortcut = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Integer)

    full_time = db.Column(db.Integer, nullable=False)
