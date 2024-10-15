from flask import render_template, request, redirect, url_for, flash
from chamber_app.models.library import Composition, Composer, Instrument
from chamber_app.models.structure import Student, Teacher
from chamber_app.models.ensemble import Ensemble, EnsemblePlayer
from chamber_app.extensions import db
from . import ensemble_bp
from sqlalchemy import func, or_  # Corrected import

def generate_ensemble_name_composition(composition):
    # Detect ensemble type based on the number of players required by the composition
    num_players = len(composition.players)
    
    if num_players == 2:
        ensemble_type = "Duo"
    elif num_players == 3:
        ensemble_type = "Trio"
    elif num_players == 4:
        ensemble_type = "Quartet"
    else:
        ensemble_type = "Ensemble"
    
    # Count existing ensembles of this type and append the next number
    existing_ensembles = Ensemble.query.filter(Ensemble.name.like(f"{ensemble_type}%")).all()
    next_number = len(existing_ensembles) + 1
    
    return f"{ensemble_type} {next_number}"

def generate_ensemble_name_count(num_players):
    
    if num_players == 2:
        ensemble_type = "Duo"
    elif num_players == 3:
        ensemble_type = "Trio"
    elif num_players == 4:
        ensemble_type = "Kvarteto"
    elif num_players == 5:
        ensemble_type = "Kvinteto"
    elif num_players == 6:
        ensemble_type = "Sexteto"
    elif num_players == 7:
        ensemble_type = "Septeto"
    else:
        ensemble_type = "Komorní soubor"
    
    # Count existing ensembles of this type and append the next number
    existing_ensembles = Ensemble.query.filter(Ensemble.name.like(f"{ensemble_type}%")).all()
    next_number = len(existing_ensembles) + 1
    
    return f"{ensemble_type} {next_number}"

def create_ensemble_student_based(students):
    new_ensemble = Ensemble(
        name=generate_ensemble_name_count(len(students))
    )
    try:
        db.session.add(new_ensemble)
        db.session.commit()
    except Exception as e:
        flash(f"Stala se chyba: {e}", "danger") 
    for student in students:
        selected_student = Student.query.filter_by(id=student).first()
        new_ensemble_member = EnsemblePlayer(
            ensemble_id=new_ensemble.id,
            student_id=selected_student.id,
            instrument_id=selected_student.instrument.id
        )
        db.session.add(new_ensemble_member)
        print(f"Adding student: {selected_student.first_name} {selected_student.last_name} to the ensemble")
    db.session.commit()
    flash(f"Přidán nový komorní soubor pod jménem: {new_ensemble.name}", "success")

def create_ensemble_composition_based(composition):
    new_ensemble = Ensemble(
        name=generate_ensemble_name_composition(composition)
    )
    db.session.add(new_ensemble)
    print("New ensemble added")
    for player in composition.players:
        new_ensemble_player = Ensemble(
            ensemble_id=new_ensemble.id,
        )
        db.session.add(new_ensemble_player)
    db.session.commit()
    print("All players added")
        
def get_ensemble_instrumentation(ensemble_id):
    ensemble = Ensemble.query.filter_by(id=ensemble_id).first()
    instruments = []
    
    for player in ensemble.ensemble_players:
        if player.student_id:
            # Check if player.instruments is not None and is iterable
            if player.instruments:  # This assumes instruments is a list or similar
                instruments.extend(player.instruments)  # Ensure you're using 'instruments' (plural)

    # Sort instruments by the 'order' attribute
    sorted_instruments = sorted(instruments, key=lambda instrument: instrument.order)
    return sorted_instruments


def rename_ensemble(ensemble_id):
    ensemble = Ensemble.query.filter_by(id=ensemble_id).first()
    player_count = ensemble.count_ensemble_players
    new_name = generate_ensemble_name_count(player_count)
    ensemble.name=new_name
    db.session.commit()
    print("Ensemble edited")


@ensemble_bp.route('/')
def show_ensembles():
    ensembles = Ensemble.query.all()
    return render_template('ensembles.html', ensembles=ensembles)

@ensemble_bp.route('/detail/<int:ensemble_id>')
def ensemble_detail(ensemble_id):
    ensemble = Ensemble.query.filter_by(id=ensemble_id).first()
    return render_template('ensemble_detail.html', ensemble=ensemble)
@ensemble_bp.route('/delete/<int:ensemble_id>', methods=["POST"])
def delete_ensemble(ensemble_id):
    ensemble = Ensemble.query.filter_by(id=ensemble_id).first()
    ensemble.teacher = None  # Clear the association if necessary
    
    try:
        # Delete all players associated with the ensemble
        for player in ensemble.ensemble_players:
            db.session.delete(player)

        # Now delete the ensemble
        db.session.delete(ensemble)
        db.session.commit()  # Commit after all deletions

        flash(f"Komorní soubor {ensemble.name} odstraněn.", "success")
    except Exception as e:
        db.session.rollback()  # Rollback if there's an error
        flash(f"Vyskytla se chyba: {e}", "danger")
    
    return redirect(url_for('ensemble.show_ensembles'))


@ensemble_bp.route('/<int:ensemble_id>/assign_composition/', methods=["GET", "POST"])
def assign_composition(ensemble_id):
    # Get the ensemble by ID
    ensemble = Ensemble.query.get_or_404(ensemble_id)
    compositions = Composition.query.all()
    
    if request.method == "POST":
        try:
            selected_composition = request.form.get('selected_composition')
            ensemble.composition_id = selected_composition
            db.session.commit()
            flash("Composition assigned successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Vyskytla se chyba: {e}", "danger")
        return redirect(url_for('ensemble.ensemble_detail', ensemble_id=ensemble.id))

    return render_template('assign_composition.html', compositions=compositions, ensemble=ensemble)

@ensemble_bp.route('/<int:ensemble_id>/unassign_composition/', methods=["POST"])
def unassign_composition(ensemble_id):
    # Get the ensemble by ID
    ensemble = Ensemble.query.filter_by(id=ensemble_id).first()
    
    if request.method == "POST":
        ensemble.composition_id = None
        db.session.commit()
        print("Composition assigned successfully")
        return redirect(url_for('ensemble.ensemble_detail', ensemble_id=ensemble.id))

@ensemble_bp.route('/unassign_student/<int:ensemble_player_id>', methods=["POST"])
def unassign_student(ensemble_player_id):
    if request.method == "POST":
        ensemble_player = EnsemblePlayer.query.get_or_404(ensemble_player_id)
        ensemble_player.student_id = None
        # Commit the change to the database
        db.session.commit()

        # Return a success message or redirect
        print('Student successfully unassigned from the ensemble.')
        return redirect(url_for('ensemble.ensemble_detail', ensemble_id=ensemble_player.ensemble_id))

@ensemble_bp.route('/assign_student/<int:ensemble_player_id>', methods=["GET", "POST"])
def assign_student(ensemble_player_id):
    ensemble_player = EnsemblePlayer.query.filter_by(id=ensemble_player_id).first()
    students = Student.query.all()

    if request.method == "POST":
        selected_student = request.form.get('selected_student')

        # # Check if the student is already part of the ensemble
        # for player in ensemble_current_players:
        #     if player.student_id == int(selected_student):
        #         print("This student is already in the ensemble!")
        #         # Redirect back to the detail page immediately
        #         return redirect(url_for("ensemble.ensemble_detail", ensemble_id=ensemble_player.ensemble_id))

        # If the student is not found in the ensemble, assign them
        try:    
            ensemble_player.student_id = selected_student
            db.session.commit()
            flash("Student added to the ensemble", "success")
        except Exception as e:
            flash(f"Vyskytla se chyba {e}", "danger")
        return redirect(url_for("ensemble.ensemble_detail", ensemble_id=ensemble_player.ensemble_id))

    return render_template("assign_student.html", ensemble_player=ensemble_player, students=students)

@ensemble_bp.route('assign_teacher/<int:ensemble_id>', methods=["GET", "POST"])
def assign_teacher(ensemble_id):
    ensemble = Ensemble.query.filter_by(id=ensemble_id).first()
    teachers = Teacher.query.all()
    if request.method == "POST":
        selected_teacher = request.form.get('selected_teacher')
        ensemble.teacher_id = selected_teacher
        db.session.commit()
        print("Teacher assigned")
        return redirect(url_for('ensemble.ensemble_detail', ensemble_id=ensemble.id))
    return render_template('assign_teacher.html', ensemble=ensemble, teachers=teachers)

@ensemble_bp.route('/<int:ensemble_id>/ensemble_player/add', methods=["POST"])
def add_ensemble_player(ensemble_id):
    new_ensemble_player = EnsemblePlayer(
        ensemble_id=ensemble_id
    )
    db.session.add(new_ensemble_player)
    db.session.commit()
    rename_ensemble(ensemble_id)
    print("New player added to the Ensemble")
    return redirect(url_for("ensemble.ensemble_detail", ensemble_id=ensemble_id))

@ensemble_bp.route('/delete/ensemble_player/<int:ensemble_player_id>', methods=["POST"])
def delete_ensemble_player(ensemble_player_id):
    if request.method == "POST":
        ensemble_player = EnsemblePlayer.query.filter_by(id=ensemble_player_id).first()
        ensemble_id = ensemble_player.ensemble_id
        db.session.delete(ensemble_player)
        db.session.commit()
        rename_ensemble(ensemble_id)
        print("Ensemble player deleted")
        return redirect(url_for("ensemble.ensemble_detail", ensemble_id=ensemble_id))

@ensemble_bp.route('wizard')
def ensemble_wizard():
    return render_template('ensemble_wizard.html')

@ensemble_bp.route('/add/composition_based', methods=['GET', 'POST'])
def add_composition_based():
    instruments = request.args.getlist('instruments')
    durations = request.args.getlist('durations')

    # Base query for compositions
    query = Composition.query

    # Filter by instruments if any are selected
    if instruments:
        query = query.join(Composition.instruments).filter(Instrument.id.in_(instruments))

    # Filter by duration ranges
    if durations:
        duration_filters = []
        if '0-5' in durations:
            duration_filters.append(Composition.durata.between(0, 5))
        if '5-10' in durations:
            duration_filters.append(Composition.durata.between(5, 10))
        if '10-15' in durations:
            duration_filters.append(Composition.durata.between(10, 15))
        if '15-20' in durations:
            duration_filters.append(Composition.durata.between(15, 20))
        if '20+' in durations:
            duration_filters.append(Composition.durata > 20)

        if duration_filters:
            query = query.filter(or_(*duration_filters))

    compositions = query.all()

    # Prepare selected filter names for display in the UI
    selected_instrument_names = [Instrument.query.get(inst_id).name for inst_id in instruments]
    selected_duration_ranges = [duration for duration in durations]
    
    if request.method == "POST":
        pass

    return render_template('add_ensemble_composition_based.html', compositions=compositions,
                           instruments=Instrument.query.all(), 
                           selected_instrument_names=selected_instrument_names,
                           selected_duration_ranges=selected_duration_ranges,
                           )

@ensemble_bp.route('/add/student_based', methods=['GET', 'POST'])
def add_ensemble_student_based():
    students = Student.query.all()
    if request.method == "POST":
        selected_students = request.form.getlist('selected_students')  # Get the selected student IDs as a list
        if selected_students:
            # Process the selected students, e.g., add them to an ensemble or another logic
            create_ensemble_student_based(selected_students)

            # Example: Redirect after processing
            return redirect(url_for('ensemble.show_ensembles'))
        else:
            # Handle the case where no students were selected
            return redirect(url_for('ensemble.add_ensemble_student_based'))

    return render_template('add_ensemble_student_based.html', students=students)