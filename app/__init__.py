import os

from flask import Flask, render_template
from config import Config
from app.models import db, User
from app.utils import current_user, difficulty_color, status_color, format_date, format_duration

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
    app.config['SECRET_KEY'] = Config.SECRET_KEY

    db.init_app(app)

    from .routes import visit
    app.register_blueprint(visit)

    app.jinja_env.globals.update(
        difficulty_color=difficulty_color,
        status_color=status_color,
        format_date=format_date,
        format_duration=format_duration,
    )

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user())

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    with app.app_context():
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if db_uri.startswith("sqlite:///"):
            db_path = db_uri[len("sqlite:///"):]
            instance_dir = os.path.dirname(db_path)
            if instance_dir:
                os.makedirs(instance_dir, exist_ok=True)

        db.create_all()
        _seed_admin(app)

    return app

def _seed_admin(app):
    if User.query.filter_by(role="admin").first():
        return
    admin = User(
        full_name="System Administrator",
        name=Config.ADMIN_USERNAME,
        email=Config.ADMIN_EMAIL,
        contact=None,
        role="admin",
    )
    admin.set_pass_hash(Config.ADMIN_PASSWORD)
    db.session.add(admin)
    db.session.commit()
