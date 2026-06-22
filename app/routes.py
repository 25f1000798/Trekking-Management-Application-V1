from flask import (
    Blueprint,
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash
)

from .models import User,Treks,Bookings,Staff
from datetime import datetime

visit = Blueprint("visit",__name__,static_folder="../static" ,template_folder="../templates")

# routes
@visit.route("/login",methods=["POST","GET"])
def index():
    if request.method == "POST":
        name = request.form["user_name"]
        email = request.form["user_email"]
        password = request.form["user_pass"]
        # filter_by takes keyword args do not just pass .filter_by(email) pass .filter_by(email=email)
        _user = User.query.filter_by(email=email).first()

        if name == _user.name and email==_user.email and _user.check_pass_hash(password):
            return "<h1>Congrats login is successful</h1>"
        else:
            flash("Something is wrong")
            return "<h1>Credentials are invalid</h1>"
    return render_template('login.html')

