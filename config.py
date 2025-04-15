import os
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env file
load_dotenv(Path(__file__).parent/'.env')

class Config:
    # Use getenv() instead of direct dictionary access
    SECRET_KEY = os.getenv('SECRET_KEY')  # No more KeyError risk
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    SQLALCHEMY_DATABASE_URI = os.getenv('internal_url')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')