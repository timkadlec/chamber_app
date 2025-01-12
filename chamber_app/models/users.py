from flask_login import UserMixin
from chamber_app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class UserRoles(db.Model):
    """Association model to manage the many-to-many relationship between User and Role."""
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    date_assigned = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships for accessing related User and Role objects
    user = db.relationship('User', back_populates='user_roles')
    role = db.relationship('Role', back_populates='user_roles')


class UserModule(db.Model):
    """Association model to manage the many-to-many relationship between User and Module."""
    __tablename__ = 'user_modules'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    date_assigned = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships for accessing related User and Role objects
    user = db.relationship('User', back_populates='user_modules')
    module = db.relationship('Module', back_populates='user_modules')


class Role(db.Model):
    """Role model for defining different roles within the application."""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    user_roles = db.relationship('UserRoles', back_populates='role', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role {self.name}>"

    @property
    def all_users(self):
        users = User.query.join(UserRoles).filter(UserRoles.role_id == self.id).all()
        return users


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
    user_roles = db.relationship('UserRoles', back_populates='user', cascade="all, delete-orphan")
    user_modules = db.relationship('UserModule', back_populates='user', cascade="all, delete-orphan")

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

    def has_role(self, role_name):
        """Check if the user has a specific role."""
        return any(user_role.role.name == role_name for user_role in self.user_roles)

    def has_module(self, module_name):
        """Check if the user has access to a specific module or is an admin."""
        if self.is_admin():  # Check if user is admin
            return True
        # Check if the user has the module by checking the relationship
        return any(user_module.module and user_module.module.name == module_name for user_module in self.user_modules)

    def is_admin(self):
        """Check if the user has the admin role."""
        return self.has_role('admin')


class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_modules = db.relationship('UserModule', back_populates='module', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role {self.name}>"

    @property
    def all_users(self):
        users = []
        user_modules = UserModule.query.filter_by(module_id=self.id).all()
        for u in user_modules:
            user = User.query.filter_by(id=u.user_id).first()
            users.append(user)
        return users
