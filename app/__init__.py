from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
from flask_migrate import Migrate



db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    migrate = Migrate(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.auth import auth as auth_blueprint
    from app.views import main as main_blueprint
    from app.api import api as api_blueprint


    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api')
  



    with app.app_context():
        db.create_all()
        

    return app

