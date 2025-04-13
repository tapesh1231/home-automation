import os

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Fallback if not set in the environment
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'another-secret')  # Fallback salt
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')  # Fallback if not set
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    if os.environ.get('FLASK_ENV') == 'production':
        SESSION_COOKIE_SECURE = True  # Requires HTTPS in production
        REMEMBER_COOKIE_SECURE = True
    else:
        SESSION_COOKIE_SECURE = False  # Disable for development without HTTPS
        REMEMBER_COOKIE_SECURE = False
    
    # Flask-Login
    SESSION_PROTECTION = 'strong'
    
    # Application
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')  # Default to production if not set
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', False)  # Default to False if not set
