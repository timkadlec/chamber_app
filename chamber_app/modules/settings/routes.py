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
)
from chamber_app.models.library import Instrument
from chamber_app.models.ensemble import EnsemblePlayer


# Helper functions to get or create entries
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


def get_or_create_teacher(name):
    teacher = Teacher.query.filter_by(name=name).first()
    if teacher is not None:
        return teacher
    else:
        teacher = Teacher(name=name)
        db.session.add(teacher)
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

            # Extract required columns
            required_columns = [
                "Příjmení",
                "Jméno",
                "Osobní čís.",
                "Název oboru/specializace",
                "Školitel",
                "Oborová katedra",
                "T",
                "Roč",
                "StS",
                "K"
            ]
            df_filtered = df[required_columns]
            try:
                new_students = []
                for _, row in df_filtered.iterrows():

                    # Create or get related entries
                    instrument = get_or_create_instrument(row["Název oboru/specializace"])
                    teacher = (
                        get_or_create_teacher(row["Školitel"])
                        if pd.notna(row["Školitel"]) and row["Školitel"].strip() != ""
                        else None
                    )
                    department = get_or_create_department(row["Oborová katedra"])
                    study_program = get_or_create_study_program(row["T"])
                    student_status = get_student_status(row["StS"])
                    class_year = get_class_year(row["Roč"], study_program.id)
                    active = False if row["K"] == "N" else True

                    # Create a new student object
                    student_db = Student(
                        last_name=row["Příjmení"],
                        first_name=row["Jméno"],
                        osobni_cislo=row["Osobní čís."],
                        department_id=department.id,
                        teacher_id=teacher.id if teacher else None,
                        active=active,
                        guest=False,
                        student_status_id=student_status.id,
                        instrument_id=instrument.id,
                        study_program_id=study_program.id,
                        class_year_id=class_year.id,
                    )
                    new_students.append(student_db)

                
                db.session.add_all(new_students)
                db.session.commit()
                flash(f"{len(new_students)} students added or updated successfully.","success",)
            except Exception as e:
                db.session.rollback()
                flash(
                    "An error occurred while saving to the database: " + str(e),
                    "danger",
                )

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
