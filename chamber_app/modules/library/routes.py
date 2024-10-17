from flask import render_template, request, redirect, url_for, jsonify, abort, flash
from . import library_bp
from chamber_app.models.library import (
    Composer,
    Composition,
    Instrument,
    Player,
    composition_player
)
from chamber_app.models.structure import Nationality
from chamber_app.forms import ComposerForm, CompositionForm
from chamber_app.extensions import db
import os
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename


@library_bp.route("/composers")
def show_composers():
    form_composer = ComposerForm()
    form_composer.populate_nationalities()
    nationalities = Nationality.query.all()
    composers = Composer.query.order_by(Composer.last_name).all()
    return render_template("composers.html",
                           composers=composers,
                           nationalities=nationalities,
                           form_composer=form_composer)


@library_bp.route("/composer/add", methods=["POST"])
def add_composer():
    form_composer = ComposerForm()
    form_composer.populate_nationalities()
    if form_composer.validate_on_submit():
        new_composer = Composer(
            first_name=form_composer.first_name.data,
            last_name=form_composer.last_name.data,
            birth_date=form_composer.birth_date.data,
            death_date=form_composer.death_date.data,
            musical_period=form_composer.musical_period.data,
            nationality_id=form_composer.nationality.data
        )
        try:
            db.session.add(new_composer)
            db.session.commit()
            flash(f"Skladatel {new_composer.first_name} {new_composer.last_name} úspešně založen", "success")
            return redirect(url_for("library.composer_detail", composer_id=new_composer.id))
        except Exception as e:
            flash(f"Vyskytla se chyba: {e}", "danger")

    errors = form_composer.errors
    return jsonify({'success': False, 'error': errors})


@library_bp.route("/composer/import", methods=["POST"])
def import_composer():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join("/tmp", filename)
    file.save(file_path)

    try:
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            last_name = row["Last Name"]
            first_name = row["First Name"]
            birth_date = row["Date of Birth"]
            death_date = row["Date of Death"]
            musical_period = row["Musical Period"]
            nationality = row.get("State", None)

            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
            if isinstance(death_date, str) or isinstance(death_date, pd.Timestamp):
                death_date = (
                    datetime.strptime(death_date, "%Y-%m-%d").date()
                    if death_date.strip()
                    else None
                )
            elif pd.isna(death_date):
                death_date = None

            existing_composer = Composer.query.filter_by(
                first_name=first_name, last_name=last_name
            ).first()
            if existing_composer:
                continue

            composer = Composer(
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                death_date=death_date,
                musical_period=musical_period,
                nationality=nationality,
            )
            db.session.add(composer)

        db.session.commit()
        print("Composers imported successfully")
        return redirect(url_for("library.show_composers"))

    except Exception as e:
        db.session.rollback()
        print(str(e))
        return redirect(url_for("library.show_composers"))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@library_bp.route("composer/detail/<int:composer_id>")
def composer_detail(composer_id):
    composer = Composer.query.get(composer_id)

    if composer is None:
        abort(404)

    return render_template("composer_detail.html", composer=composer)


@library_bp.route("/compositions", methods=["GET"])
def show_compositions():
    form = ComposerForm()
    selected_instruments = request.args.getlist("instruments")
    selected_durations = request.args.getlist("durations")

    query = Composition.query

    # Instrument filter
    selected_instrument_names = []
    if selected_instruments:
        selected_instruments = [
            int(instrument_id) for instrument_id in selected_instruments
        ]
        selected_instrument_names = [
            instrument.name for instrument in Instrument.query.filter(Instrument.id.in_(selected_instruments)).all()
        ]
        query = query.join(Composition.players).filter(
            Player.instruments.any(Instrument.id.in_(selected_instruments))
        ).group_by(Composition.id).having(
            db.func.count(Player.id) == len(selected_instruments)
        )

    # Duration filter
    selected_duration_ranges = []
    duration_filters = []
    if "0-5" in selected_durations:
        duration_filters.append(Composition.durata <= 5)
        selected_duration_ranges.append("0-5 min")
    if "5-10" in selected_durations:
        duration_filters.append(db.and_(Composition.durata > 5, Composition.durata <= 10))
        selected_duration_ranges.append("5-10 min")
    if "10-15" in selected_durations:
        duration_filters.append(db.and_(Composition.durata > 10, Composition.durata <= 15))
        selected_duration_ranges.append("10-15 min")
    if "15-20" in selected_durations:
        duration_filters.append(db.and_(Composition.durata > 15, Composition.durata <= 20))
        selected_duration_ranges.append("15-20 min")
    if "20+" in selected_durations:
        duration_filters.append(Composition.durata > 20)
        selected_duration_ranges.append("20+ min")

    if duration_filters:
        query = query.filter(db.or_(*duration_filters))

    compositions = query.all()

    instruments = Instrument.query.order_by(Instrument.order).all()

    return render_template(
        "compositions.html",
        compositions=compositions,
        instruments=instruments,
        form=form,
        selected_instrument_names=selected_instrument_names,
        selected_duration_ranges=selected_duration_ranges,
    )


@library_bp.route("/composition/add", methods=["GET", "POST"])
def add_composition():
    form_composition = CompositionForm()
    form_composer = ComposerForm()
    if form_composition.validate_on_submit():
        new_composition = Composition(
            name=form_composition.name.data,
            durata=form_composition.durata.data,
            composer_id=form_composition.composer_id.data,
        )
        db.session.add(new_composition)
        db.session.commit()
        print("Composition added successfully")
        return redirect(
            url_for("library.edit_players", composition_id=new_composition.id)
        )

    if form_composer.validate_on_submit():
        new_composer = Composer(
            first_name=form_composer.first_name.data,
            last_name=form_composer.last_name.data,
            birth_date=form_composer.birth_date.data,
            death_date=form_composer.death_date.data,
            musical_period=form_composer.musical_period.data,
            nationality=form_composer.nationality.data
        )
        db.session.add(new_composer)
        db.session.commit()

    return render_template("add_composition.html", form_composition=form_composition, form_composer=form_composer)


@library_bp.route('composition/<int:composition_id>/delete', methods=['POST'])
def delete_composition(composition_id):
    composition = Composition.query.filter_by(id=composition_id).first()
    for player in composition.players:
        db.session.delete(player)
    db.session.delete(composition)
    db.session.commit()
    print("Composition deleted")
    return redirect(url_for('library.show_compositions'))


@library_bp.route("/composition/<int:composition_id>/edit_players", methods=["GET", "POST"])
def edit_players(composition_id):
    # Fetch the composition
    composition = Composition.query.get_or_404(composition_id)

    if request.method == "POST":
        # Get the form data
        role = request.form.get('role')  # Assuming you have a field for role in your form
        instrument_ids = request.form.getlist('instruments')

        # Create a new player
        new_player = Player(
            role=role if role else None
        )
        db.session.add(new_player)

        # Assign instruments to the player
        for instrument_id in instrument_ids:
            instrument = Instrument.query.get(instrument_id)
            if instrument:
                new_player.instruments.append(instrument)

        # Associate the new player with the composition along with the role
        composition.players.append(new_player)



        # Commit the changes
        db.session.commit()

        # Redirect to the edit page after adding the player
        return redirect(url_for('library.edit_players', composition_id=composition_id))

    # In case of a GET request, render the template with the current composition and instruments
    instruments = Instrument.query.all()  # Assuming you have a model for instruments
    return render_template('edit_players.html', composition=composition, instruments=instruments)


@library_bp.route("composition/<int:composition_id>/player/<int:player_id>/delete", methods=['POST'])
def delete_player(composition_id, player_id):
    # Retrieve the player by ID
    player = Player.query.filter_by(id=player_id).first()

    if player:
        # Delete the player if found
        db.session.delete(player)
        db.session.commit()
    else:
        # Optional: handle the case where the player does not exist
        print('Player not found!', 'error')

    # Redirect to the edit players page
    return redirect(url_for('library.edit_players', composition_id=composition_id))


@library_bp.route("/composition/detail/<int:composition_id>", methods=["GET", "POST"])
def composition_detail(composition_id):
    composition = Composition.query.get_or_404(composition_id)
    composition.players.sort(key=lambda x: x.id)
    return render_template("composition_detail.html", composition=composition)


@library_bp.route("/get_instruments", methods=["GET"])
def get_instruments():
    instruments = Instrument.query.all()
    instrument_choices = [(inst.id, inst.name) for inst in instruments]
    return jsonify(instrument_choices)
