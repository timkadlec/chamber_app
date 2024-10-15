from flask import render_template, request, redirect, url_for, flash
from . import structure_bp
from chamber_app.extensions import db
import os
import pandas as pd
from chamber_app.models.structure import Department, Student, Teacher
from chamber_app.models.library import Instrument


@structure_bp.route('/students')
def show_students():
    students = Student.query.order_by(Student.last_name).all()
    return render_template("students.html", students=students)


@structure_bp.route('/teachers')
def show_teachers():
    teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template("teachers.html", teachers=teachers)
