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
    name = db.Column(db.String(256), unique=True, nullable=False)
    durata = db.Column(db.Float, nullable=False)
    composer_id = db.Column(db.Integer, ForeignKey('composers.id'), nullable=False)

    composer = relationship('Composer', back_populates='compositions')
    players = relationship('Player',
                           secondary=composition_player,
                           back_populates='compositions')

    @property
    def composer_full_name(self):
        return f"{self.composer.first_name} {self.composer.last_name}"

    @property
    def player_count(self):
        return len(self.players)

    @property
    def instrumentation_text(self):
        instrument_count = {}

        # Count how many players play each instrument
        for player in self.players:
            for instrument in player.instruments:
                # Only count normal (not obligatory) instruments
                if instrument.name in instrument_count:
                    instrument_count[instrument.name] += 1
                else:
                    instrument_count[instrument.name] = 1

        # Create a list of instruments and their counts
        instrument_list = [(name, count) for name, count in instrument_count.items()]

        # Get order values for the instruments
        ordered_instruments = []
        for instrument_name, count in instrument_list:
            instrument = Instrument.query.filter_by(name=instrument_name).first()
            order = instrument.order if instrument else float('inf')  # Use float('inf') if not found
            ordered_instruments.append((instrument_name, count, order))

        # Sort instruments by their order attribute
        ordered_instruments.sort(key=lambda x: x[2])  # Sort by the order (3rd element in tuple)

        # Prepare the output based on counts
        output = []
        for instrument_name, count, _ in ordered_instruments:
            if count == 1:
                output.append(f"{instrument_name}")  # Omit "x" for a single instrument
            else:
                output.append(f"{count} x {instrument_name}")  # Include "x" for multiple instruments

        # Join everything with commas and return
        return ', '.join(output)

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
    role = db.Column(db.String(256))

    # Relationship to link players with their instruments
    instruments = relationship('Instrument',
                               secondary=player_instrument,
                               back_populates='players')

    # Relationship to link players with compositions
    compositions = relationship('Composition',
                                secondary=composition_player,
                                back_populates='players')


class Instrument(db.Model):
    __tablename__ = 'instrument'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    order = db.Column(db.String(20))
    is_obligatory = db.Column(Boolean, default=False)  # Added to distinguish between main and obligatory instruments

    # Relationship to link instruments with players
    players = relationship('Player',
                           secondary=player_instrument,
                           back_populates='instruments')

    # Optional: Self-referential relationship if you want to track main and obligatory instruments
    main_instrument_id = db.Column(db.Integer, ForeignKey('instrument.id'), nullable=True)
    main_instrument = relationship('Instrument', remote_side=[id], backref='obligatory_instruments')
