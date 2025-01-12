from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, IntegerField, SelectField, FloatField, HiddenField, \
    PasswordField, EmailField, DecimalField
from wtforms.validators import DataRequired, Optional, ValidationError, NumberRange, Length, EqualTo
from chamber_app.models.library import Composer, Instrument
from chamber_app.models.structure import Nationality, Teacher, AcademicPosition
from chamber_app.models.ensemble import Ensemble


class ComposerForm(FlaskForm):
    first_name = StringField('Jméno', validators=[DataRequired()])
    last_name = StringField('Příjmení', validators=[DataRequired()])
    birth_date = DateField('Datum narození (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    death_date = DateField('Datum skonu (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    musical_period = StringField('Hudební období', validators=[Optional()])
    nationality = SelectField('Národnost', coerce=int, validators=[Optional()])
    submit = SubmitField('Vytvořit skladatele')

    def __init__(self, *args, **kwargs):
        super(ComposerForm, self).__init__(*args, **kwargs)
        self.populate_nationalities()

    def populate_nationalities(self):
        self.nationality.choices = [(n.id, n.name) for n in Nationality.query.all()]


class CompositionForm(FlaskForm):
    name = StringField('Název skladby', validators=[DataRequired(), Length(max=256)])
    durata = FloatField('Durata (minuty)', validators=[DataRequired(), NumberRange(min=0)])
    composer_id = SelectField('Skladatel', coerce=int, validators=[DataRequired()])

    submit = SubmitField('Založit skladbu')

    def __init__(self, *args, **kwargs):
        super(CompositionForm, self).__init__(*args, **kwargs)

        # Populate the composer choices
        self.composer_id.choices = [(composer.id, f"{composer.last_name} {composer.first_name}") for composer in
                                    Composer.query.order_by(Composer.last_name).all()]


class InstrumentationForm(FlaskForm):
    instrument_id = SelectField('Nástroj', choices=[], validators=[DataRequired()])
    quantity = IntegerField('Počet', validators=[DataRequired(), NumberRange(min=1)])
    player_id = SelectField('Hráč', choices=[], validators=[DataRequired()])  # New field for player selection
    submit = SubmitField('Uložit instrumentaci')


class PlayerForm(FlaskForm):
    player_name = StringField('Hráč', validators=[DataRequired()])
    instrument_id = SelectField('Nástroj', choices=[], validators=[DataRequired()])
    add_player = SubmitField('Přidat hráče')


class AddGuestForm(FlaskForm):
    first_name = StringField("Jméno", validators=[DataRequired()])
    last_name = StringField("Příjmení", validators=[DataRequired()])
    instrument_id = SelectField('Nástroj', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(AddGuestForm, self).__init__(*args, **kwargs)
        # Dynamically populate choices from the database
        self.populate_instruments(self)

    def populate_instruments(self, obj):
        self.instrument_id.choices = [(i.id, i.name) for i in Instrument.query.all()]


class InstrumentSelectForm(FlaskForm):
    instrument_id = SelectField('Nástroj', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(InstrumentSelectForm, self).__init__(*args, **kwargs)
        # Dynamically populate choices from the database
        self.populate_instruments(self)

    def populate_instruments(self, obj):
        self.instrument_id.choices = [(i.id, i.name) for i in Instrument.query.order_by(Instrument.order).all()]


class HourDonationForm(FlaskForm):
    hour_donation = SelectField('Hodinová dotace', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(HourDonationForm, self).__init__(*args, **kwargs)
        # Dynamically populate choices from the database
        self.populate_hour_donation(self)

    def populate_hour_donation(self, obj):
        self.hour_donation.choices = [i for i in range(1, 5)]


class TeacherChamberAssignmentForm(FlaskForm):
    teacher_id = SelectField('Pedagog', coerce=int, validators=[DataRequired()])
    hour_donation = SelectField('Hodinová dotace', coerce=int, validators=[DataRequired()])

    def __init__(self, ensemble_id=None, *args, **kwargs):
        super(TeacherChamberAssignmentForm, self).__init__(*args, **kwargs)
        self.populate_teachers()
        if ensemble_id:
            self.populate_hour_donation(ensemble_id)

    def populate_teachers(self):
        # Populate teachers from the Teacher model
        self.teacher_id.choices = [(i.id, i.name) for i in Teacher.query.order_by(Teacher.name).all()]

    def populate_hour_donation(self, ensemble_id):
        ensemble = Ensemble.query.get(ensemble_id)
        self.hour_donation.choices = [(i, f"{i} hodiny") for i in range(1, ensemble.remaining_hour_donation + 1)]


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=150)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=150)])
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class EditTeacherForm(FlaskForm):
    name = StringField('Jméno pedagoga', validators=[DataRequired(), Length(min=1, max=150)])
    academic_position_id = SelectField('Akademický pozice', coerce=int, validators=[DataRequired()])
    employment_time = FloatField("Úvazek")  # Optional to avoid issues with empty fields
    submit = SubmitField('Uložit')

    def __init__(self, *args, **kwargs):
        super(EditTeacherForm, self).__init__(*args, **kwargs)
        # Dynamically populate choices from the database
        self.populate_academic_positions(self)

    def populate_academic_positions(self, obj):
        self.academic_position_id.choices = [(p.id, p.name) for p in AcademicPosition.query.all()]


class AcademicYearForm(FlaskForm):
    start = DateField()
    end = DateField()
    submit = SubmitField('Založit')


class AddRoleForm(FlaskForm):
    name = StringField("Název role", validators=[DataRequired()])
    submit = SubmitField("Vytvořit")


class AddModuleForm(FlaskForm):
    name = StringField("Název modulu", validators=[DataRequired()])
    submit = SubmitField("Vytvořit")
