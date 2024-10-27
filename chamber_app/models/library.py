from chamber_app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Integer, String, Float, Table, Boolean

# Association table for the many-to-many relationship between players and instruments
player_instrument = db.Table('player_instrument',
                             db.Column('player_id', db.Integer, ForeignKey('players.id'), primary_key=True),
                             db.Column('instrument_id', db.Integer, ForeignKey('instrument.id'), primary_key=True)
                             )

# Association table for the many-to-many relationship between players and compositions
composition_player = db.Table('composition_player',
                              db.Column('composition_id', db.Integer, ForeignKey('compositions.id'), primary_key=True),
                              db.Column('player_id', db.Integer, ForeignKey('players.id'), primary_key=True),
                              )


def group_instruments_by_id(instruments):
    grouped_instruments = {}

    for instrument in instruments:
        instrument_id = instrument.id
        if instrument_id not in grouped_instruments:
            grouped_instruments[instrument_id] = []
        grouped_instruments[instrument_id].append(instrument)

    return grouped_instruments


class Composer(db.Model):
    __tablename__ = 'composers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    death_date = db.Column(db.Date, nullable=True)  # Set to nullable
    musical_period = db.Column(db.String(256), nullable=True)

    nationality_id = db.Column(db.Integer, db.ForeignKey('nationalities.id'))

    nationality = relationship("chamber_app.models.structure.Nationality", backref='composers', lazy=True)
    compositions = relationship('Composition', back_populates='composer')

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"


class Composition(db.Model):
    __tablename__ = 'compositions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    durata = db.Column(db.Float, nullable=False)
    youtube_link = db.Column(db.String(256))
    composer_id = db.Column(db.Integer, ForeignKey('composers.id'), nullable=False)

    composer = relationship('Composer', back_populates='compositions')
    players = relationship('Player',
                           secondary=composition_player,
                           back_populates='compositions')
    ensemble_assignments = relationship('chamber_app.models.ensemble.EnsembleAssignment', back_populates='composition')

    @property
    def composer_full_name(self):
        return f"{self.composer.first_name} {self.composer.last_name}"

    @property
    def player_count(self):
        return len(self.players)

    @property
    def instrumentation_text(self):
        """Returns a dictionary where the key is the Instrument object, sorted by 'order',
        and the value is a list of all players associated with that instrument."""
        instrument_player_dict = {}

        # Group players by instruments
        for player in self.players:
            instrument = player.instrument  # Get the instrument for the player
            if instrument not in instrument_player_dict:
                instrument_player_dict[instrument] = []  # Initialize list for this instrument
            instrument_player_dict[instrument].append(player)  # Add player to the instrument's list

        # Sort the dictionary by the 'order' attribute of Instrument
        sorted_instrument_player_dict = dict(
            sorted(instrument_player_dict.items(), key=lambda item: item[0].order)
        )
        instrumentation_text = ""
        dict_length = len(sorted_instrument_player_dict)

        for index, (key, value) in enumerate(sorted_instrument_player_dict.items()):
            if len(value) == 1:
                if index == dict_length - 1:  # Last iteration
                    instrumentation_text += f"{key.name}"
                else:
                    instrumentation_text += f"{key.name}, "
            else:
                if index == dict_length - 1:  # Last iteration
                    instrumentation_text += f"{len(value)} {key.name}"
                else:
                    instrumentation_text += f"{len(value)} {key.name}, "

        return instrumentation_text

    @property
    def instrumentation_list(self):
        instruments = []
        for player in self.players:
            for instrument in player.instruments:
                if instrument not in instruments:
                    instruments.extend(player.instruments)  # Append all instruments from each player

        # Sort instruments by the 'order' attribute
        sorted_instruments = sorted(instruments, key=lambda instrument: instrument.order)
        return sorted_instruments


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    prefix = db.Column(db.String(256))
    suffix = db.Column(db.String(256))
    # Relationship to link players with their instruments
    instrument_id = db.Column(db.Integer, ForeignKey('instrument.id'), nullable=True)

    # Relationship to link players with compositions
    compositions = relationship('Composition',
                                secondary=composition_player,
                                back_populates='players')
    instrument = relationship("Instrument", back_populates="players")


class Instrument(db.Model):
    __tablename__ = 'instrument'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    shortcut = db.Column(db.String(15))
    order = db.Column(db.String(20))

    # Relationship to link instruments with players
    players = relationship('Player', back_populates='instrument')
