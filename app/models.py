from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer,primary_key= True)
    name = db.Column(db.String(256),nullable= False)
    email = db.Column(db.String(256),nullable= False,unique = True)
    pass_hash = db.Column(db.String(1000),nullable=False)
    contact = db.Column(db.String(13),nullable = True)
    # keep it last
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at =  db.Column(db.DateTime,default=datetime.utcnow)

    bookings = db.relationship(
    "Bookings",
    backref="user",
    cascade="all, delete-orphan")

    # methods
    def set_pass_hash(self,password) -> None:
        self.pass_hash = generate_password_hash(password)

    def check_pass_hash(self,password) -> bool:
        return check_password_hash(self.pass_hash,password)
    
    def __repr__(self):
        return f"{self.id} : {self.email} : {self.name}"

class Staff(db.Model):
    __tablename__ = "staff"

    id  = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(256), nullable= False)
    email = db.Column(db.String(256), nullable=False, unique = True)
    pass_hash = db.Column(db.String(256), nullable= False)
    created_at =  db.Column(db.DateTime,default=datetime.utcnow)

    treks_assigned = db.relationship("Treks",backref = "staff")


    def set_pass_hash(self,password) -> None:
        self.pass_hash = generate_password_hash(password)

    def check_pass_hash(self,password) -> bool:
        return check_password_hash(self.pass_hash,password)
    
    def __repr__(self):
        return f"{self.id} : {self.email} : {self.name}"

class Treks(db.Model):
    __tablename__ = "trek"

    # attributes
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(256), nullable= False, index = True)
    location = db.Column(db.String(50), nullable= False, index = True)
    difficulty= db.Column(db.String(50), nullable = False, index = True)
    status = db.Column(db.String(50), nullable = False)
    duration =  db.Column(db.Integer, nullable= False)
    starting_date = db.Column(db.Date, nullable= False)
    ending_date = db.Column(db.Date, nullable= False)
    
    is_blocked = db.Column(db.String(50),nullable = False,default = False)
    # records    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    capacity = db.Column(db.Integer, default = 10)
    available = db.Column(db.Integer, default = 10)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relations
    assigned_staff_id = db.Column(db.Integer,db.ForeignKey("staff.id"),nullable = False)
    bookings = db.relationship(
    "Bookings",
    backref="trek",
    cascade="all, delete-orphan")


    def __repr__(self):
        return f"{self.id} : {self.name} : {self.location}"

class Bookings(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False, index= True)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable = False, index= True)
    booked_at = db.Column(db.DateTime , default = datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="booked", index=True)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"{self.id} : {self.user_id} : {self.trek_id}"
