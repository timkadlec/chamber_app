import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

class DevelopmentConfig(Config):
    DEBUG = True
