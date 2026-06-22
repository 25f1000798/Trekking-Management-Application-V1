from flask import Flask
from config import Config
# from app.models import db # both work same
from app.models import User,Staff,Treks,Bookings,db


def create_app():
    app = Flask(__name__,template_folder="../templates",static_folder="../static")
    # app config first then initialization
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    
    db.init_app(app)

    with app.app_context():
        db.create_all()
        
        u1 = User(
            name = "Demo1",
            email = "demo@example.com",
            pass_hash = ("demo123")
        )
        u1.set_pass_hash(u1.pass_hash)
        # db.session.add(u1)
        # db.session.commit()

    return app
