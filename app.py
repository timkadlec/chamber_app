from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
from config import Config
from extensions import db, migrate  # Use the Flask SQLAlchemy extension here
import os
from models import Major, Instrument, Teacher, Department, Student  # Assuming models are defined in a separate file

# Flask app setup
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)

# Helper functions to get or create entries
def get_or_create_department(name):
    department = Department.query.filter_by(name=name).first()
    if department is not None:
        return department
    else:
        department = Department(name=name)
        db.session.add(department)
        db.session.commit()
    

def get_or_create_instrument(name):
    instrument = Instrument.query.filter_by(name=name).first()
    if name is not None:
        return instrument
    else:
        instrument = Instrument(name=name)
        db.session.add(instrument)
        db.session.commit()

def get_or_create_teacher(name):
    teacher = Teacher.query.filter_by(name=name).first()
    if teacher is not None:
        return teacher
    else:
        teacher = Teacher(name=name)
        db.session.add(teacher)
        db.session.commit()


@app.route('/')
def home_view():
    students = Student.query.order_by(Student.prijmeni).all()
    return render_template("index.html", students=students)

# File upload handling
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
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
            required_columns = ["Příjmení", "Jméno", "Osobní čís.", "Název oboru/specializace", "Školitel", "Oborová katedra"]
            df_filtered = df[required_columns]

            # Add students and their details to the database
            new_students = []
            for _, row in df_filtered.iterrows():
                # Check if the student already exists
                if Student.query.filter_by(osobni_cislo=row['Osobní čís.']).first():
                    flash(f"Student with Osobní číslo {row['Osobní čís.']} already exists, skipping.")
                    continue

                # Get or create related entities
                instrument = get_or_create_instrument(row['Název oboru/specializace'])

                # Skip if 'Školitel' is None or empty
                if pd.isna(row['Školitel']) or row['Školitel'].strip() == '':
                    teacher = None  # No teacher assigned
                else:
                    teacher_name = row['Školitel']
                    teacher = get_or_create_teacher(teacher_name)

                department_id = get_or_create_department(row['Oborová katedra'])

                # Add student to the database
                student_db = Student(
                    prijmeni=row['Příjmení'],
                    jmeno=row['Jméno'],
                    osobni_cislo=row['Osobní čís.'],
                    department_id=department_id.id,
                    teacher_id=teacher.id if teacher else None,  # Add skolitel_id only if available
                    instrument_id=instrument.id,
                )
                db.session.add(student_db)
                new_students.append(student_db)

            # Commit to save to the database
            db.session.commit()

            # Redirect to the page showing newly added records
            print('File processed and data added to the database.')
            return redirect(url_for('show_new_students', student_ids=[student.id for student in new_students]))

    return render_template('upload.html')

# Route to display newly added students
@app.route('/new-students', methods=['GET'])
def show_new_students():
    # Get student IDs from the query parameters
    student_ids = request.args.getlist('student_ids', type=int)
    
    # Fetch the newly added students from the database
    new_students = Student.query.filter(Student.id.in_(student_ids)).all()
    
    return render_template('new_students.html', students=new_students)

# Route to display newly added students
@app.route('/students', methods=['GET'])
def show_students():
    # Get student IDs from the query parameters
    students = Student.query.order_by(Student.prijmeni).all()
    
    return render_template('new_students.html', students=students)


@app.route('/teachers', methods=['GET'])
def show_teachers():
    # Query all teachers (Školitel) from the database
    teachers = Skolitel.query.order_by(Skolitel.name).all()
    
    # Render the template and pass the list of teachers
    return render_template('teachers.html', teachers=teachers)

@app.route('/departments', methods=['GET'])
def show_departments():
    # Query all departments (OborovaKatedra) from the database
    departments = OborovaKatedra.query.all()
    
    # Render the template and pass the list of departments
    return render_template('departments.html', departments=departments)

@app.route('/specializations', methods=['GET'])
def show_specializations():
    # Query all specializations (Instrument) from the database
    specializations = Instrument.query.order_by(Instrument.name).all()
    
    # Render the template and pass the list of specializations
    return render_template('specializations.html', specializations=specializations)

if __name__ == '__main__':
    app.run(debug=True)
