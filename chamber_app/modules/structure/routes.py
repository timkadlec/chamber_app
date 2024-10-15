from flask import render_template
from . import structure_bp
from chamber_app.extensions import db
from chamber_app.models.structure import Student, Teacher


@structure_bp.route('/students')
def show_students():
    students = Student.query.filter_by(active=True, guest=False).order_by(Student.last_name).all()
    return render_template("students.html", students=students)


@structure_bp.route('/teachers')
def show_teachers():
    teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template("teachers.html", teachers=teachers)
