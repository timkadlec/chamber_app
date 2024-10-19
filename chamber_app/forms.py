from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, IntegerField, SelectField, FloatField, FieldList, FormField
from wtforms.validators import DataRequired, Optional, ValidationError, NumberRange, Length
from chamber_app.models.library import Composer, Instrument
from chamber_app.models.structure import Nationality


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