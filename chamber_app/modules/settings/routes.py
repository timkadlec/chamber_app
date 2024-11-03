from flask import render_template, request, redirect, url_for, flash
from . import settings_bp
from chamber_app.extensions import db
import os
import pandas as pd
from chamber_app.models.structure import (
    Department,
    Student,
    Teacher,
    StudyProgram,
    ClassYear,
    StudentStatus,
    TeacherDepartment,
    AcademicYear,
    Semester
)
from chamber_app.models.library import Instrument
from chamber_app.models.ensemble import EnsemblePlayer
from chamber_app.forms import AcademicYearForm


def get_or_create_department(name):
    department = Department.query.filter_by(name=name).first()
    if department is not None:
        return department
    else:
        department = Department(name=name)
        db.session.add(department)
        db.session.commit()
        return department


def get_or_create_instrument(name):
    instrument = Instrument.query.filter_by(name=name).first()
    if instrument is not None:
        return instrument
    else:
        instrument = Instrument(name=name, is_obligatory=False)
        db.session.add(instrument)
        db.session.commit()
        return instrument


def get_or_create_teacher(import_name, department):
    # TODO Also assign a department belonging to the student as well
    teacher = Teacher.query.filter_by(import_name=import_name).first()
    if teacher is not None:
        return teacher
    else:
        teacher = Teacher(import_name=import_name)
        db.session.add(teacher)
        db.session.commit()
        teacher_department = TeacherDepartment(
            teacher_id=teacher.id,
            department_id=department.id
        )
        db.session.add(teacher_department)
        db.session.commit()

        return teacher


def get_or_create_study_program(name):
    study_program = StudyProgram.query.filter_by(name=name).first()
    if study_program is not None:
        return study_program
    else:
        study_program = StudyProgram(
            name=name
        )  # Adjust according to your model definition
        db.session.add(study_program)
        db.session.commit()
        return study_program


def get_class_year(year_number, study_program_id):
    class_year = ClassYear.query.filter_by(
        number=year_number, study_program_id=study_program_id
    ).first()
    return class_year


def get_student_status(shortcut):
    student_status = StudentStatus.query.filter_by(shortcut=shortcut).first()
    if student_status:
        return student_status
    else:
        return None


@settings_bp.route("/import_students", methods=["GET", "POST"])
def import_students():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file and file.filename.endswith(".xlsx"):
            # Save the uploaded file temporarily
            file_path = os.path.join("uploaded_file.xlsx")
            file.save(file_path)

            # Process the file
            df = pd.read_excel(file_path)

            required_columns = [
                "Příjmení",
                "Jméno",
                "Osobní čís.",
                "Název oboru/specializace",
                "Školitel",
                "Oborová katedra",
                "T",
                "Roč",
                "StS"
            ]

            # If "K" column is present, include it in required columns
            if "K" in df.columns:
                required_columns.append("K")

            df_filtered = df[required_columns]
            try:
                new_students = []
                for _, row in df_filtered.iterrows():
                    # Create or get related entries
                    instrument = get_or_create_instrument(row["Název oboru/specializace"])
                    department = get_or_create_department(row["Oborová katedra"])
                    teacher = (
                        get_or_create_teacher(row["Školitel"], department)
                        if pd.notna(row["Školitel"]) and row["Školitel"].strip() != ""
                        else None
                    )

                    study_program = get_or_create_study_program(row["T"])
                    student_status = get_student_status(row["StS"])
                    class_year = get_class_year(row["Roč"], study_program.id)
                    active = True  # Default to active if "K" is not present
                    if "K" in df.columns and pd.notna(row.get("K")):
                        active = False if row["K"] == "N" else True
                    # Check if the student already exists
                    student_db = Student.query.filter_by(osobni_cislo=row["Osobní čís."]).first()

                    if student_db:
                        # Update the existing student's details
                        student_db.last_name = row["Příjmení"]
                        student_db.first_name = row["Jméno"]
                        student_db.department_id = department.id

                        # Check if teacher, student_status, and class_year are found before assigning
                        student_db.teacher_id = teacher.id if teacher else None
                        student_db.active = active
                        student_db.guest = False
                        student_db.student_status_id = student_status.id if student_status else None
                        student_db.instrument_id = instrument.id
                        student_db.study_program_id = study_program.id
                        student_db.class_year_id = class_year.id if class_year else None
                    else:
                        # Create a new student object
                        student_db = Student(
                            last_name=row["Příjmení"],
                            first_name=row["Jméno"],
                            osobni_cislo=row["Osobní čís."],
                            department_id=department.id,
                            teacher_id=teacher.id if teacher else None,
                            active=active,
                            guest=False,
                            student_status_id=student_status.id if student_status else None,
                            instrument_id=instrument.id,
                            study_program_id=study_program.id,
                            class_year_id=class_year.id if class_year else None,
                        )

                    new_students.append(student_db)

                # After processing all students, commit the changes
                db.session.add_all(new_students)
                db.session.commit()

                flash(f"{len(new_students)} studentů bylo přidáno nebo aktualizováno.", "info", )
            except Exception as e:
                db.session.rollback()
                flash(f"Vyskytla se chyba: {e} ", "danger", )

            # Remove the temporary file
            os.remove(file_path)

            # Redirect to the page showing newly added records
            return redirect(
                url_for(
                    "structure.show_students",
                    student_ids=[student.id for student in new_students],
                )
            )

    return render_template("import_students.html")


def delete_student(student):
    student_to_delete = Student.query.filter_by(id=student.id).first()
    student_in_ensembles = EnsemblePlayer.query.filter_by(student_id=student.id).all()
    for ensemble_student in student_in_ensembles:
        ensemble_student.student_id = None
    db.session.delete(student_to_delete)
    db.session.commit()


@settings_bp.route("/delete_students", methods=["POST"])
def delete_students():
    students = Student.query.all()
    for student in students:
        delete_student(student)
    flash("Všichni studenti vymazáni", "success")
    return redirect(url_for("settings.import_students"))


@settings_bp.route('academic-years', methods=["GET", "POST"])
def academic_years():
    form = AcademicYearForm()
    years = AcademicYear.query.all()
    if form.validate_on_submit():
        new_year = AcademicYear(
            start=form.start.data,
            end=form.end.data
        )
        db.session.add(new_year)
        db.session.commit()
        # zimni semestr
        zs = Semester(
            name="ZS",
            order=1,
            academic_year_id=new_year.id
        )
        db.session.add(zs)
        ls = Semester(
            name="LS",
            order=2,
            academic_year_id=new_year.id
        )
        db.session.add(ls)
        db.session.commit()

    return render_template('academic_years.html',
                           form=form,
                           years=years)
