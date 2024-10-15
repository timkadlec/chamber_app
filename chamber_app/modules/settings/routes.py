from flask import render_template, request, redirect, url_for, flash
from . import settings_bp
from chamber_app.extensions import db
import os
import pandas as pd
from chamber_app.models.structure import Department, Student, Teacher, StudyProgram, Year
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
        study_program = StudyProgram(name=name)  # Adjust according to your model definition
        db.session.add(study_program)
        db.session.commit()
        return study_program

def get_or_create_year(year_number, study_program_id):
    year = Year.query.filter_by(year=year_number, study_program_id=study_program_id).first()
    if year is not None:
        return year
    else:
        year = Year(year=year_number, study_program_id=study_program_id)
        db.session.add(year)
        db.session.commit()
        return year

def delete_student(student):
    student_to_delete = Student.query.filter_by(id=student.id).first()
    student_in_ensembles = EnsemblePlayer.query.filter_by(student_id=student.id).all()
    for ensemble_student in student_in_ensembles:
        ensemble_student.student_id = None
    db.session.delete(student_to_delete)
    db.session.commit()

@settings_bp.route('/import_students', methods=['GET', 'POST'])
def import_students():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and file.filename.endswith('.xlsx'):
            # Save the uploaded file temporarily
            file_path = os.path.join('uploaded_file.xlsx')
            file.save(file_path)

            # Process the file
            df = pd.read_excel(file_path)

            # Extract required columns
            required_columns = ["Příjmení", "Jméno", "Osobní čís.", "Název oboru/specializace", "Školitel", "Oborová katedra", "T", "Roč"]
            df_filtered = df[required_columns]

            new_students = []
            for _, row in df_filtered.iterrows():
                # Check if the student already exists
                existing_student = Student.query.filter_by(osobni_cislo=row['Osobní čís.']).first()

                # Create or get related entries
                instrument = get_or_create_instrument(row['Název oboru/specializace'])
                teacher = get_or_create_teacher(row['Školitel']) if pd.notna(row['Školitel']) and row['Školitel'].strip() != '' else None
                department = get_or_create_department(row['Oborová katedra'])
                study_program = get_or_create_study_program(row['T'])
                year = get_or_create_year(row['Roč'], study_program.id)

                # Update or create a new student object
                if existing_student:
                    # Check if the student needs to be reassigned to a higher year
                    if existing_student.year_id != year.id:
                        # If the existing year is lower, update the year_id
                        existing_student.year_id = year.id
                    
                    # Update only the fields that are missing
                    existing_student.last_name = row['Příjmení'] if existing_student.last_name != row['Příjmení'] else existing_student.last_name
                    existing_student.first_name = row['Jméno'] if existing_student.first_name != row['Jméno'] else existing_student.first_name
                    existing_student.department_id = department.id if existing_student.department_id != department.id else existing_student.department_id
                    existing_student.teacher_id = teacher.id if teacher and existing_student.teacher_id != teacher.id else existing_student.teacher_id
                    existing_student.instrument_id = instrument.id if existing_student.instrument_id != instrument.id else existing_student.instrument_id
                    existing_student.study_program_id = study_program.id if existing_student.study_program_id != study_program.id else existing_student.study_program_id
                    
                    # Add the updated student to the session
                    db.session.add(existing_student)
                else:
                    # Create a new student object
                    student_db = Student(
                        last_name=row['Příjmení'],
                        first_name=row['Jméno'],
                        osobni_cislo=row['Osobní čís.'],
                        department_id=department.id,
                        teacher_id=teacher.id if teacher else None,
                        instrument_id=instrument.id,
                        study_program_id=study_program.id,
                        year_id=year.id
                    )
                    db.session.add(student_db)
                    new_students.append(student_db)

            try:
                db.session.commit()
                print(f'{len(new_students)} students added or updated successfully.')
            except Exception as e:
                db.session.rollback()
                print('An error occurred while saving to the database: ' + str(e))

            # Remove the temporary file
            os.remove(file_path)

            # Redirect to the page showing newly added records
            return redirect(url_for('structure.show_students', student_ids=[student.id for student in new_students]))

    return render_template('import_students.html')

@settings_bp.route('/delete_students', methods=['POST'])
def delete_students():
    students = Student.query.all()
    for student in students:
        delete_student(student)
    print("all students deleted")
    return redirect(url_for('settings.import_students'))