from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, IntegerField, SelectField, FloatField, FieldList, FormField
from wtforms.validators import DataRequired, Optional, ValidationError, NumberRange, Length
from chamber_app.models.library import Composer, Instrument

class ComposerForm(FlaskForm):
    first_name = StringField('Jméno', validators=[DataRequired()])
    last_name = StringField('Příjmení', validators=[DataRequired()])
    birth_date = DateField('Datum narození (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    death_date = DateField('Datum skonu (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    musical_period = StringField('Hudební období', validators=[Optional()])
    nationality = StringField('Národnost', validators=[Optional()])
    submit = SubmitField('Vytvořit skladatele')

    # Custom validation method to check for duplicate composer based on name and birth date
    def validate_first_name(self, field):
        composer = Composer.query.filter_by(
            first_name=field.data,
            last_name=self.last_name.data,
            birth_date=self.birth_date.data
        ).first()

        if composer:
            raise ValidationError(f'A composer named {field.data} {self.last_name.data} with the same birth date already exists.')

class CompositionForm(FlaskForm):
    name = StringField('Název skladby', validators=[DataRequired(), Length(max=256)])
    durata = FloatField('Durata (minuty)', validators=[DataRequired(), NumberRange(min=0)])
    composer_id = SelectField('Skladatel', coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Založit skladbu')
    
    def __init__(self, *args, **kwargs):
        super(CompositionForm, self).__init__(*args, **kwargs)
        
        # Populate the composer choices
        self.composer_id.choices = [(composer.id, f"{composer.last_name} {composer.first_name}") for composer in Composer.query.order_by(Composer.last_name).all()]
        
class InstrumentationForm(FlaskForm):
    instrument_id = SelectField('Nástroj', choices=[], validators=[DataRequired()])
    quantity = IntegerField('Počet', validators=[DataRequired(), NumberRange(min=1)])
    player_id = SelectField('Hráč', choices=[], validators=[DataRequired()])  # New field for player selection
    submit = SubmitField('Uložit instrumentaci')
    
class PlayerForm(FlaskForm):
    player_name = StringField('Hráč', validators=[DataRequired()])
    instrument_id = SelectField('Nástroj', choices=[], validators=[DataRequired()])
    add_player = SubmitField('Přidat hráče')
