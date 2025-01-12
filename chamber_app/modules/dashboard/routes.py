from flask import render_template, request, session, redirect, url_for
from . import dashboard_bp
from ...extensions import db
from ...models.structure import Student, StudentChamberAssignment


@dashboard_bp.route('/')
def home_view():
    students_without_active_assignments = (
        db.session.query(Student)
        .outerjoin(Student.chamber_assignments)  # Use outer join to include students without assignments
        .filter(StudentChamberAssignment.ended.is_(None))  # Check that ended is None
        .filter(Student.chamber_assignments == None)
        .filter(Student.guest == False)# Ensure no assignments exist
        .order_by(Student.last_name)
        .distinct()  # Get distinct students
        .all()
    )
    return render_template("dashboard_index.html", students=students_without_active_assignments)


@dashboard_bp.route('/set-active-academic-year', methods=['POST'])
def set_active_academic_year():
    active_value = request.form.get('active')  # Get the selected value from the form
    if active_value:
        session['active_academic_year'] = active_value
        print(session['active_academic_year'])
        return redirect(url_for('dashboard.home_view'))  # Redirect back to the dashboard
    return "No active value provided", 400
