from flask_login import UserMixin
from chamber_app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    """
    User model for storing user information in the database.

    Attributes:
        id (int): A unique identifier for each user in the database.
        username (str): The username chosen by the user, which must be unique.
        password_hash (str): A hashed representation of the user's password.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        email (str): The email address of the user.
        role (str): The role of the user within the application (e.g., admin, student).
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Increase length to 255
    first_name = db.Column(db.String(150), nullable=True)
    last_name = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(50), nullable=True)

    def set_password(self, password):
        """Hashes the password and stores it in the database.

        Args:
            password (str): The plaintext password to be hashed.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hashed password.

        Args:
            password (str): The plaintext password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)
