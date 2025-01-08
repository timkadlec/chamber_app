from flask import render_template, request, redirect, url_for, flash, abort
from chamber_app.models.library import Composition, Composer, Instrument
from chamber_app.models.structure import Student, Teacher, TeacherChamberAssignment, StudentChamberAssignment
from chamber_app.models.ensemble import Ensemble, EnsemblePlayer, EnsembleAssignment, EnsemblePerformance
from chamber_app.extensions import db
from chamber_app.forms import InstrumentSelectForm, HourDonationForm, TeacherChamberAssignmentForm
from . import ensemble_bp
from sqlalchemy import func, or_  # Corrected import
from datetime import datetime
from itertools import chain
from markupsafe import Markup
from flask_login import current_user


def name_ensemble(num_players):
    if num_players == 2:
        return "Duo"
    elif num_players == 3:
        return "Trio"
    elif num_players == 4:
        return "Kvarteto"
    elif num_players == 5:
        return "Kvinteto"
    elif num_players == 6:
        return "Sexteto"
    elif num_players == 7:
        return "Septeto"
    else:
        return "Komorní soubor"


def generate_ensemble_name_composition(composition):
    # Detect ensemble type based on the number of players required by the composition
    num_players = len(composition.players)

    ensemble_type = name_ensemble(num_players)

    # Count existing ensembles of this type and append the next number
    existing_ensembles = Ensemble.query.filter(Ensemble.name.like(f"{ensemble_type}%")).all()
    next_number = len(existing_ensembles) + 1

    return f"{ensemble_type} {next_number}"


def generate_ensemble_name_count(num_players):
    ensemble_type = name_ensemble(num_players)
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


def create_empty_ensemble():
    new_ensemble = Ensemble(
        name=generate_ensemble_name_count(2)
    )
    try:
        db.session.add(new_ensemble)
        db.session.commit()
        for student in range(2):
            new_ensemble_member = EnsemblePlayer(
                ensemble_id=new_ensemble.id,
            )
            db.session.add(new_ensemble_member)
        db.session.commit()
        flash(f"Přidán nový komorní soubor pod jménem: {new_ensemble.name}", "success")
        return new_ensemble
    except Exception as e:
        flash(f"Stala se chyba: {e}", "danger")


def create_ensemble_composition_based(composition_id):
    assigned_composition = Composition.query.filter_by(id=composition_id).first()
    # Create ensemble model
    new_ensemble = Ensemble(
        name=generate_ensemble_name_composition(assigned_composition)
    )
    db.session.add(new_ensemble)
    db.session.commit()
    flash("Nový soubor založen", "success")

    # Assign composition as assignment
    new_assignment = EnsembleAssignment(
        ensemble_id=new_ensemble.id,
        composition_id=assigned_composition.id
    )
    db.session.add(new_assignment)
    db.session.commit()
    print("Composition assigned")
    # create players
    for player in assigned_composition.players:
        new_ensemble_player = EnsemblePlayer(
            ensemble_id=new_ensemble.id,
            instrument_id=player.instrument_id
        )
        db.session.add(new_ensemble_player)
        print(player.instrument_id)
    db.session.commit()
    print("All players added")
    return new_ensemble


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
    ensemble.name = new_name
    db.session.commit()
    print("Ensemble edited")


def delete_ensemble(ensemble_id):
    try:
        teacher_assignments = TeacherChamberAssignment.query.filter_by(ensemble_id=ensemble_id).all()
        for assignment in teacher_assignments:
            db.session.delete(assignment)

        ensemble_assignments = EnsembleAssignment.query.filter_by(ensemble_id=ensemble_id).all()
        for assignment in ensemble_assignments:
            db.session.delete(assignment)

        ensemble_players = EnsemblePlayer.query.filter_by(ensemble_id=ensemble_id).all()
        for player in ensemble_players:
            student_assignments = StudentChamberAssignment.query.filter_by(ensemble_player_id=player.id).all()
            for assignment in student_assignments:
                db.session.delete(assignment)
            db.session.delete(player)

        ensemble = Ensemble.query.get_or_404(ensemble_id)
        db.session.delete(ensemble)
        db.session.commit()
        flash(f"Komorní soubor kompletně odstraněn.", "success")
    except Exception as e:
        db.session.rollback()  # Rollback if there's an error
        flash(f"Vyskytla se chyba: {e}", "danger")


def ensemble_activities(ensemble_id):
    ensemble = Ensemble.query.filter_by(id=ensemble_id).first()
    activities = []

    # Fetch assignments
    ensemble_assignments = EnsembleAssignment.query.filter_by(ensemble_id=ensemble_id).all()
    student_assignments = StudentChamberAssignment.query.filter(
        StudentChamberAssignment.ensemble_player_id.in_([player.id for player in ensemble.ensemble_players])
    ).all()
    teacher_assignments = TeacherChamberAssignment.query.filter_by(ensemble_id=ensemble_id).all()

    # Combine all assignments
    combined_assignments = list(chain(ensemble_assignments, student_assignments, teacher_assignments))
    sorted_assignments = sorted(
        combined_assignments,
        key=lambda entry: entry.created if entry.created is not None else datetime.min,
        reverse=True  # Sorts in descending order
    )

    for a in sorted_assignments:
        if isinstance(a, EnsembleAssignment):
            if a.created:
                activities.append({
                    'date': a.created,
                    'type': 'composition',
                    'details': Markup('Zadána skladba <b>{}: {}</b>').format(a.composition.composer_full_name,
                                                                             a.composition.name)
                })
            if a.ended:
                activities.append({
                    'date': a.ended,
                    'type': 'composition',
                    'details': Markup('Ukončeno studium skladby <b>{}: {}</b>').format(a.composition.composer_full_name,
                                                                                       a.composition.name)
                })
        elif isinstance(a, StudentChamberAssignment):
            if a.created:
                activities.append({
                    'date': a.created,
                    'type': 'student',
                    'details': (
                        Markup('Přiřazen student <b>{} {}, {}</b>').format(a.student.first_name, a.student.last_name,
                                                                           a.student.instrument.name)
                        if not a.student.guest else
                        Markup('Přiřazen host <b>{} {}, {}</b>').format(a.student.first_name, a.student.last_name,
                                                                        a.student.instrument.name))
                })
            if a.ended:
                activities.append({
                    'date': a.ended,
                    'type': 'student',
                    'details': (
                        Markup('Odebrán student <b>{} {}, {}</b>').format(a.student.first_name, a.student.last_name,
                                                                          a.student.instrument.name)
                        if not a.student.guest else
                        Markup('Odebrán host <b>{} {}, {}</b>').format(a.student.first_name, a.student.last_name,
                                                                       a.student.instrument.name))
                })
        elif isinstance(a, TeacherChamberAssignment):
            if a.created:
                activities.append({
                    'date': a.created,
                    'type': 'teacher',
                    'details': Markup('Přiřazen profesor <b>{}</b>').format(a.teacher.name)
                })
            if a.ended:
                activities.append({
                    'date': a.ended,
                    'type': 'teacher',
                    'details': Markup('Odebrán profesor <b>{}</b>').format(a.teacher.name)
                })

    # Sort activities by date
    activities.sort(key=lambda x: x['date'], reverse=True)  # In-place sorting
    return activities  # Return the sorted list


@ensemble_bp.route('/')
def show_ensembles():
    ensembles = Ensemble.query.all()
    return render_template('ensembles.html', ensembles=ensembles)


@ensemble_bp.route('/detail/<int:ensemble_id>')
def ensemble_detail(ensemble_id):
    instrument_form = InstrumentSelectForm()
    hour_donation_form = HourDonationForm()
    teacher_assignment_form = TeacherChamberAssignmentForm(ensemble_id=ensemble_id)
    ensemble = Ensemble.query.filter_by(id=ensemble_id).first()
    ensemble_activities_list = ensemble_activities(ensemble_id)
    return render_template('ensemble_detail.html',
                           ensemble=ensemble,
                           ensemble_activities_list=ensemble_activities_list,
                           instrument_form=instrument_form,
                           hour_donation_form=hour_donation_form,
                           teacher_assignment_form=teacher_assignment_form)


@ensemble_bp.route('/delete/<int:ensemble_id>', methods=["POST"])
def ensemble_delete(ensemble_id):
    delete_ensemble(ensemble_id)
    return redirect(url_for('ensemble.show_ensembles'))


@ensemble_bp.route('/<int:ensemble_id>/hour_donation/set', methods=["POST"])
def set_hour_donation(ensemble_id):
    form = HourDonationForm()
    if form.validate_on_submit():
        ensemble = Ensemble.query.get_or_404(ensemble_id)
        ensemble.hour_donation = form.hour_donation.data
        db.session.commit()
        flash(f"Hodinová dotace pro soubor {ensemble.name} byla nastavena na {form.hour_donation.data}", 'success')
        return redirect(url_for('ensemble.ensemble_detail', ensemble_id=ensemble.id))
    flash("Chyba při ukládání hodinové dotace.", 'danger')
    return redirect(url_for('ensemble.ensemble_detail', ensemble_id=ensemble_id))


@ensemble_bp.route('/player/<int:player_id>/assign_instrument', methods=['POST'])
def assign_player_instrument(player_id):
    form = InstrumentSelectForm()
    player = EnsemblePlayer.query.filter_by(id=player_id).first()
    if form.validate_on_submit():
        player.instrument_id = form.instrument_id.data  # Use the form data
        db.session.commit()
        return redirect(url_for('ensemble.ensemble_detail', ensemble_id=player.ensemble_id))
    # Handle invalid form (optional)
    return redirect(url_for('ensemble.ensemble_detail', ensemble_id=player.ensemble_id))


@ensemble_bp.route('/<int:ensemble_id>/assign_composition/', methods=["GET", "POST"])
def assign_composition(ensemble_id):
    ensemble = Ensemble.query.get_or_404(ensemble_id)
    compositions = Composition.query.all()

    if request.method == "POST":
        try:
            selected_composition_id = request.form.get('selected_composition')
            new_ensemble_assignment = EnsembleAssignment(
                ensemble_id=ensemble_id,
                composition_id=selected_composition_id
            )
            db.session.add(new_ensemble_assignment)
            db.session.commit()
            flash("Composition assigned successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Vyskytla se chyba: {e}", "danger")
        return redirect(url_for('ensemble.ensemble_detail', ensemble_id=ensemble.id))

    return render_template('assign_composition.html', compositions=compositions, ensemble=ensemble)


@ensemble_bp.route('/unassign_composition/<int:ensemble_assignment_id>', methods=["POST"])
def unassign_composition(ensemble_assignment_id):
    a = EnsembleAssignment.query.filter_by(id=ensemble_assignment_id).first()
    a.ended = datetime.utcnow()
    db.session.commit()
    print("Composition assigned successfully")
    return redirect(url_for('ensemble.ensemble_detail', ensemble_id=a.ensemble_id))


@ensemble_bp.route('/assign_student/<int:ensemble_player_id>', methods=["GET", "POST"])
def assign_student(ensemble_player_id):
    ensemble_player = EnsemblePlayer.query.get_or_404(ensemble_player_id)
    students = Student.query.filter_by(instrument_id=ensemble_player.instrument_id, guest=0).all()

    if request.method == "POST":
        selected_student_id = request.form.get('selected_student')
        try:
            new_assignment = StudentChamberAssignment(
                ensemble_player_id=ensemble_player.id,
                student_id=selected_student_id
            )
            db.session.add(new_assignment)
            db.session.commit()
            flash("Student added to the ensemble", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Vyskytla se chyba {e}", "danger")
        return redirect(url_for("ensemble.ensemble_detail", ensemble_id=ensemble_player.ensemble_id))

    return render_template("assign_student.html", ensemble_player=ensemble_player, students=students)


@ensemble_bp.route('/assign_guest/<int:ensemble_player_id>', methods=["GET", "POST"])
def assign_guest(ensemble_player_id):
    ensemble_player = EnsemblePlayer.query.get_or_404(ensemble_player_id)
    guests = Student.query.filter_by(instrument_id=ensemble_player.instrument_id, guest=1).all()

    if request.method == "POST":
        selected_student_id = request.form.get('selected_guest_id')
        try:
            new_assignment = StudentChamberAssignment(
                ensemble_player_id=ensemble_player.id,
                student_id=selected_student_id
            )
            db.session.add(new_assignment)
            db.session.commit()
            flash("Guest added to the ensemble", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Vyskytla se chyba {e}", "danger")
        return redirect(url_for("ensemble.ensemble_detail", ensemble_id=ensemble_player.ensemble_id))

    return render_template("assign_guest.html", ensemble_player=ensemble_player, guests=guests)


@ensemble_bp.route('/unassign_student/<int:active_student_assignment>', methods=["POST"])
def unassign_student(active_student_assignment):
    a = StudentChamberAssignment.query.get_or_404(active_student_assignment)
    a.ended = datetime.utcnow()
    try:
        db.session.commit()
        flash('Student úspěšně odebrán z komorního souboru. Záznam o jeho členství je zachován v archivu.', "success")
    except Exception as e:
        flash(f"Vyskytla se chyba {e}", "danger")
        abort(404)
    return redirect(url_for('ensemble.ensemble_detail', ensemble_id=a.ensemble_player.ensemble_id))


@ensemble_bp.route('/<int:ensemble_id>/assign_teacher/', methods=["GET", "POST"])
def assign_teacher(ensemble_id):
    form = TeacherChamberAssignmentForm(ensemble_id=ensemble_id)  # Pass the ensemble_id here
    ensemble = Ensemble.query.filter_by(id=ensemble_id).first()

    # Ensure remaining hour donation is valid
    if ensemble and ensemble.remaining_hour_donation != 0:
        if form.validate_on_submit():
            try:
                selected_teacher_id = int(form.teacher_id.data)
                hour_donation = int(form.hour_donation.data)

                # Check for existing active assignment of the selected teacher
                existing_assignment = TeacherChamberAssignment.query.filter_by(
                    ensemble_id=ensemble.id,
                    teacher_id=selected_teacher_id,
                    ended=None  # Ensure it's active
                ).first()

                if existing_assignment:
                    # If an active assignment exists, increase the hour donation
                    existing_assignment.hour_donation += hour_donation
                    # Check if the teacher exists
                    if existing_assignment.teacher:
                        flash(
                            f"Hodinová dotace pro pedagoga {existing_assignment.teacher.name} byla zvýšena o {hour_donation}.",
                            "info")
                    else:
                        flash(f"Hodinová dotace byla zvýšena, ale pedagog nebyl nalezen.", "warning")
                else:
                    # Create a new assignment if none exists
                    teacher_assignment = TeacherChamberAssignment(
                        ensemble_id=ensemble.id,
                        teacher_id=selected_teacher_id,
                        hour_donation=hour_donation
                    )
                    db.session.add(teacher_assignment)
                    db.session.commit()  # Commit after adding a new assignment

                    # Ensure the new assignment's teacher exists
                    if teacher_assignment.teacher:
                        flash(f"Pedagog {teacher_assignment.teacher.name} byl přiřazen k souboru {ensemble.name}.",
                              "info")
                    else:
                        flash(f"Pedagog byl přiřazen, ale nebyl nalezen.", "warning")

                db.session.commit()  # Commit changes after assignment adjustment
                return redirect(url_for('ensemble.ensemble_detail', ensemble_id=ensemble.id))

            except Exception as e:
                db.session.rollback()  # Rollback in case of an error
                flash(f"Vyskytla se chybe: {e}", "danger")
    else:
        flash(f"Hodinová dotace souboru {ensemble.name} byla vyčerpána.", "danger")

    return redirect(url_for("ensemble.ensemble_detail", ensemble_id=ensemble.id))


@ensemble_bp.route('unassign_teacher/<int:teacher_assignment_id>', methods=["POST"])
def unassign_teacher(teacher_assignment_id):
    a = TeacherChamberAssignment.query.get_or_404(teacher_assignment_id)
    try:
        a.ended = datetime.utcnow()
        db.session.commit()
        flash(f"Pedagog {a.teacher.name} byl odebrán od souboru: {a.ensemble.name}. Pedagog zůstává v archivu souboru.",
              "info")
    except Exception as e:
        flash(f"Vyskytla se chybe: {e}", "danger")
    return redirect(url_for('ensemble.ensemble_detail', ensemble_id=a.ensemble.id))


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
        ensemble = Ensemble.query.filter_by(id=ensemble_player.ensemble.id).first()
        print(ensemble)
        student_assignments = StudentChamberAssignment.query.filter_by(ensemble_player_id=ensemble_player_id).all()
        for assignment in student_assignments:
            db.session.delete(assignment)
        db.session.delete(ensemble_player)
        db.session.commit()
        rename_ensemble(ensemble.id)
        print("Ensemble player deleted")
        return redirect(url_for("ensemble.ensemble_detail", ensemble_id=ensemble.id))


@ensemble_bp.route('wizard')
def ensemble_wizard():
    return render_template('ensemble_wizard.html')


@ensemble_bp.route('/create/composition_based', methods=['GET', 'POST'])
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
        selected_composition = int(request.args.get('composition_id'))
        new_ensemble = create_ensemble_composition_based(selected_composition)
        return redirect(url_for("ensemble.ensemble_detail", ensemble_id=new_ensemble.id))

    return render_template('add_ensemble_composition_based.html', compositions=compositions,
                           instruments=Instrument.query.all(),
                           selected_instrument_names=selected_instrument_names,
                           selected_duration_ranges=selected_duration_ranges,
                           )


@ensemble_bp.route('/create/student_based', methods=['GET', 'POST'])
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


@ensemble_bp.route('/create/empty', methods=['POST'])
def add_empty_ensemble():
    new_ensemble = create_empty_ensemble()
    return redirect(url_for('ensemble.ensemble_detail', ensemble_id=new_ensemble.id))
