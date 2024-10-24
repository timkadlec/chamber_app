from flask import render_template, request, redirect, url_for, flash
from . import dashboard_bp
from ...extensions import db
from ...models.structure import Student, StudentAssignment


@dashboard_bp.route('/')
def home_view():
    students_without_active_assignments = (
        db.session.query(Student)
        .outerjoin(Student.assignments)  # Use outer join to include students without assignments
        .filter(StudentAssignment.ended.is_(None))  # Check that ended is None
        .filter(Student.assignments == None)
        .filter(Student.guest == False)# Ensure no assignments exist
        .distinct()  # Get distinct students
        .all()
    )
    return render_template("dashboard_index.html", students=students_without_active_assignments)
