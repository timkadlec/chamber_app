from flask import render_template, request, session, redirect, url_for
from . import dashboard_bp
from ...extensions import db
from ...models.structure import Student, StudentChamberAssignment
from ...models.library import Instrument


@dashboard_bp.route('/')
def home_view():
    students_without_active_assignments = (
        db.session.query(Student)
        .outerjoin(Student.chamber_assignments)  # Use outer join to include students without assignments
        .filter(StudentChamberAssignment.ended.is_(None))  # Check that ended is None
        .filter(Student.chamber_assignments == None)
        .filter(Student.guest == False)# Ensure no assignments exist
        .filter(Student.active)
        .filter(Student.instrument_id != 1)
        .filter(Student.instrument_id != 2)
        .filter(Student.instrument_id != 3)
        .filter(Student.instrument_id != 8)
        .filter(Student.instrument_id != 11)
        .filter(Student.instrument_id != 9)
        .order_by(Student.last_name)
        .distinct()  # Get distinct students
        .all()
    )
    return render_template("dashboard_index.html", students=students_without_active_assignments)

