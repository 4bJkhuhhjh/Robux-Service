# app/__init__.py

from flask import Flask, session
from flask_mail import Mail
from flask_login import LoginManager
from app.models import db, User

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    @app.context_processor
    def inject_admin_flag():
        return dict(admin_logged_in=session.get("admin_logged_in", False))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        from . import routes, auth
        db.create_all()
        return app