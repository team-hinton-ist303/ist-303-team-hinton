import os
from flask_login import LoginManager
from models import User
from flask import Flask
from config import Config
from models import db
from db_cli import register_db_commands


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

   
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    register_db_commands(app)


    from auth import bp as auth_bp
    from compositions import bp as compositions_bp
    from library import bp as library_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(compositions_bp)
    app.register_blueprint(library_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app