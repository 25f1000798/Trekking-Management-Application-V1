from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer,primary_key= True)
    full_name = db.Column(db.String(256), nullable = False)
    name = db.Column(db.String(256),nullable= False)
    email = db.Column(db.String(256),nullable= False,unique = True)
    pass_hash = db.Column(db.String(1000),nullable=False)
    contact = db.Column(db.String(13),nullable = True)
    role = db.Column(db.String(50),nullable = False,default = "trekker")
    address = db.Column(db.String(256), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    # staff accounts need an admin to approve them before they can log in
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    
    # keep it last, for auth
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at =  db.Column(db.DateTime,default=datetime.utcnow)

    bookings = db.relationship(
    "Bookings",
    backref="user",
    cascade="all, delete-orphan")

    assigned_treks = db.relationship(
    "Treks",
    backref="staff_member",
    foreign_keys="Treks.assigned_staff_id")

    # methods
    def set_pass_hash(self,password) -> None:
        self.pass_hash = generate_password_hash(password)

    def check_pass_hash(self,password) -> bool:
        return check_password_hash(self.pass_hash,password)
    
    def get_role(self):
        return self.role
    
    def is_admin(self):
        return self.role == "Admin" or self.role=="admin"

    def is_staff(self):
        return self.role == "staff"

    def __repr__(self):
        return f"{self.id} : {self.email} : {self.name} : {self.role}"

class Treks(db.Model):
    __tablename__ = "trek"

    # attributes
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(256), nullable= False, index = True)
    location = db.Column(db.String(50), nullable= False, index = True)
    difficulty= db.Column(db.String(50), nullable = False, index = True)
    status = db.Column(db.String(50), nullable = False, default = "Pending")
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

    # trek info and display things
    price = db.Column(db.Float, default=0)
    altitude = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    highlights = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)


    # relations
    assigned_staff_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable = False)
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
    participants = db.Column(db.Integer, nullable=False, default=1)
    emergency_contact = db.Column(db.String(120), nullable=True)
    emergency_phone = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"{self.id} : {self.user_id} : {self.trek_id}"
