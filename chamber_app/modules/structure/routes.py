from . import structure_bp
from chamber_app.models.structure import Student, Teacher, ClassYear, Department
from chamber_app.models.library import Instrument
from flask import request, render_template, flash, redirect, url_for
from urllib.parse import urlencode
from chamber_app.forms import AddGuestForm, EditTeacherForm
from chamber_app.extensions import db


@structure_bp.route('/')
def index():
    return render_template('structure.html')


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
    students = query.filter(Student.guest == 0).all()

    return render_template("students.html",
                           students=students,
                           departments=departments,
                           instruments=instruments,
                           class_years=class_years,
                           selected_class_years=selected_class_years,
                           selected_instruments=selected_instruments,
                           selected_departments=selected_departments,
                           query_string=query_string)  # Pass selected departments to the template


@structure_bp.route('/guests', methods=['GET'])
def show_guests():
    filters = request.args.copy()
    form = AddGuestForm()

    # Pass the full URL-encoded query string to the template
    query_string = urlencode(filters)

    instruments = Instrument.query.all()

    # Get selected department IDs from the request args (list)
    selected_instruments = request.args.getlist('instruments')

    # Convert selected IDs to integers
    selected_instruments = [int(instr_id) for instr_id in selected_instruments if instr_id.isdigit()]

    # Start the query
    query = Student.query

    # Filter students based on selected instruments
    if selected_instruments:
        query = query.filter(Student.instrument_id.in_(selected_instruments))

    guests = query.filter(Student.guest == True)

    return render_template("guests.html",
                           guests=guests,
                           instruments=instruments,
                           query_string=query_string,
                           selected_instruments=selected_instruments,
                           form=form)  # Pass selected departments to the template


@structure_bp.route('/guests/add', methods=['POST'])
def add_guest():
    form = AddGuestForm()
    new_guest = Student(
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        instrument_id=form.instrument_id.data,
        guest=True
    )
    try:
        db.session.add(new_guest)
        db.session.commit()
        flash(f"Nový host jménem {new_guest.first_name} {new_guest.last_name} byl přidán", "info")
        return redirect(url_for('structure.show_guests'))
    except Exception as e:
        db.session.rollback()
        flash(f"Vyskytla se chyba: {e}", "danger")
        return redirect(url_for('structure.show_guests'))


@structure_bp.route('/teachers')
def show_teachers():
    teachers = Teacher.query.order_by(Teacher.name).all()
    edit_teacher_form = EditTeacherForm()
    return render_template("teachers.html", teachers=teachers,
                           edit_teacher_form=edit_teacher_form)


@structure_bp.route("teacher_detail/<int:teacher_id>")
def teacher_detail(teacher_id):
    teacher = Teacher.query.filter_by(id=teacher_id).first()
    edit_teacher_form = EditTeacherForm()

    # Pre-filling the form with the teacher's current details
    if teacher:
        edit_teacher_form.name.data = teacher.name
        edit_teacher_form.academic_position_id.data = teacher.academic_position_id
        edit_teacher_form.employment_time.data = teacher.employment_time

    return render_template("teacher_detail.html", teacher=teacher, edit_teacher_form=edit_teacher_form)


@structure_bp.route('teacher/<int:teacher_id>/edit', methods=['POST'])
def teacher_edit(teacher_id):
    # Create the form instance with submitted data
    edit_teacher_form = EditTeacherForm()
    # Check if the form is submitted and validated
    if request.method == "POST":
        teacher = Teacher.query.filter_by(id=teacher_id).first()
        if teacher:
            # Update teacher fields with submitted form data
            if not teacher.import_name:
                teacher.import_name = edit_teacher_form.name.data
            teacher.name = edit_teacher_form.name.data
            teacher.academic_position_id = edit_teacher_form.academic_position_id.data
            print(edit_teacher_form.employment_time.data)
            if edit_teacher_form.employment_time.data:
                teacher.employment_time = float(edit_teacher_form.employment_time.data)

            # Commit changes to the database
            db.session.commit()
            flash("Pedagog úspěšně aktualizován", "success")

            return redirect(url_for('structure.teacher_detail', teacher_id=teacher_id))
    else:
        return redirect(url_for('structure.teacher_detail', teacher_id=teacher_id))


@structure_bp.route('teacher/add', methods=['POST'])
def teacher_add():
    edit_teacher_form = EditTeacherForm()
    if not edit_teacher_form.employment_time.data:
        teacher = Teacher(
            import_name=edit_teacher_form.name.data,
            name=edit_teacher_form.name.data,
            academic_position_id=edit_teacher_form.academic_position_id.data,
        )
    else:
        teacher = Teacher(
            import_name=edit_teacher_form.name.data,
            name=edit_teacher_form.name.data,
            academic_position_id=edit_teacher_form.academic_position_id.data,
            employment_time=float(edit_teacher_form.employment_time.data)
        )
    db.session.add(teacher)
    db.session.commit()
    flash("Pedagog úspěšně přidán", "success")

    return redirect(url_for('structure.teacher_detail', teacher_id=teacher.id))
