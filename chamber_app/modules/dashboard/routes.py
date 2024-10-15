from flask import render_template, request, redirect, url_for, flash
from . import dashboard_bp

@dashboard_bp.route('/')
def home_view():
    from chamber_app.models.structure import Student
    students = Student.query.order_by(Student.last_name).all()
    return render_template("dashboard_index.html", students=students)