# 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
from flask_migrate import Migrate

# Initialize extensions (without app context)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap()

def create_app(config_class=Config):
    """Application factory to create and configure the Flask app"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    initialize_extensions(app)
    register_blueprints(app)
    configure_login_manager()
    setup_database(app)

    return app

def initialize_extensions(app):
    """Initialize Flask extensions with the application"""
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app, db)  # Note: Changed from direct assignment to init_app

def register_blueprints(app):
    """Register Flask blueprints (modular components)"""
    from app.auth import auth as auth_blueprint
    from app.views import main as main_blueprint
    from app.api import api as api_blueprint

    # Main routes
    app.register_blueprint(main_blueprint)
    
    # Authentication routes
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # API routes
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')  # Versioned API

def configure_login_manager():
    """Configure Flask-Login settings"""
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'  # Enhanced session security

def setup_database(app):
    """Initialize database and handle migrations"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # For production, you might want to handle migrations differently
        if app.config['FLASK_ENV'] == 'development':
            from flask_migrate import upgrade
            try:
                upgrade()  # Apply any pending migrations
            except Exception as e:
                app.logger.warning(f"Database migration error: {str(e)}")

# Optional: Add error handlers and other app-wide configurations
def register_error_handlers(app):
    """Register custom error handlers"""
    from flask import render_template
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500