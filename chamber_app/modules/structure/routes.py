from . import structure_bp
from chamber_app.models.structure import Student, Teacher, ClassYear, Department, StudyProgram
from chamber_app.models.library import Instrument
from flask import request, render_template
from urllib.parse import urlencode



@structure_bp.route('/students', methods=['GET'])
def show_students():
    filters = request.args.copy()

    # Pass the full URL-encoded query string to the template
    query_string = urlencode(filters)

    departments = Department.query.all()
    instruments = Instrument.query.all()
    class_years = ClassYear.query.all()

    # Get selected department IDs from the request args (list)
    selected_departments = request.args.getlist('departments')
    selected_instruments = request.args.getlist('instruments')
    selected_class_years = request.args.getlist('class_years')

    # Convert selected IDs to integers
    selected_departments = [int(dept_id) for dept_id in selected_departments if dept_id.isdigit()]
    selected_instruments = [int(instr_id) for instr_id in selected_instruments if instr_id.isdigit()]
    selected_class_years = [int(year_id) for year_id in selected_class_years if year_id.isdigit()]

    # Start the query
    query = Student.query

    # Filter students based on selected departments
    if selected_departments:
        query = query.filter(Student.department_id.in_(selected_departments))

    # Filter students based on selected instruments
    if selected_instruments:
        query = query.filter(Student.instrument_id.in_(selected_instruments))

    # Filter students based on selected class years
    if selected_class_years:
        query = query.filter(Student.class_year_id.in_(selected_class_years))

    # Execute the query and get results
    students = query.all()

    return render_template("students.html",
                           students=students,
                           departments=departments,
                           instruments=instruments,
                           class_years=class_years,
                           selected_class_years=selected_class_years,
                           selected_instruments=selected_instruments,
                           selected_departments=selected_departments,
                           query_string=query_string)  # Pass selected departments to the template


@structure_bp.route('/teachers')
def show_teachers():
    teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template("teachers.html", teachers=teachers)
