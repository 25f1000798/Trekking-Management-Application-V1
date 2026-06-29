from datetime import datetime

from flask import (
    Blueprint, render_template, request, url_for,
    redirect, flash, session, abort
)

from .models import db, User, Treks, Bookings
from .utils import (
    login_required, admin_required, staff_required, active_required,
    current_user, load_session
)

visit = Blueprint("visit", __name__, static_folder="../static", template_folder="../templates")

DIFFICULTIES = ["Easy", "Moderate", "Hard"]
TREK_STATUSES = ["Pending", "Approved", "Open", "Closed", "Completed"]


def redirect_by_role():
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("visit.admin_dashboard"))
    if role == "staff":
        return redirect(url_for("visit.staff_dashboard"))
    return redirect(url_for("visit.user_dashboard"))


# --MAIN-- routes 
@visit.route("/")
def home():
    open_treks = (
        Treks.query.filter(Treks.status.in_(["Approved", "Open"]))
        .order_by(Treks.starting_date)
        .limit(6)
        .all()
    )
    stats = {
        "treks": Treks.query.count(),
        "users": User.query.filter_by(role="trekker").count(),
        "bookings": Bookings.query.count(),
    }
    return render_template("index.html", open_treks=open_treks, stats=stats)


# --AUTH-- routes
@visit.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect_by_role()

    if request.method == "POST":
        email = request.form.get("user_email", "").strip()
        password = request.form.get("user_password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.check_pass_hash(password):
            if user.is_blacklisted:
                flash("Your account has been blacklisted. Contact admin.", "danger")
                return redirect(url_for("visit.login"))
            if user.role == "staff" and not user.is_approved:
                flash("Your staff account is pending admin approval.", "warning")
                return redirect(url_for("visit.login"))
            load_session(user)
            flash(f"Welcome back, {user.full_name or user.name}!", "success")
            return redirect_by_role()

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@visit.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect_by_role()

    if request.method == "POST":
        full_name = request.form.get("user_full_name", "").strip()
        name = request.form.get("user_name", "").strip()
        contact = request.form.get("user_contact", "").strip()
        email = request.form.get("user_email", "").strip()
        password = request.form.get("user_password", "")
        confirm = request.form.get("user_password_confirm", "")
        role = request.form.get("user_role", "trekker")

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not name or len(name) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("A valid email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if role not in ("trekker", "staff"):
            errors.append("Invalid role selected.")
        if not errors and User.query.filter_by(name=name).first():
            errors.append("That username is already taken.")
        if not errors and User.query.filter_by(email=email).first():
            errors.append("That email is already registered.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html", form_data=request.form)

        new_user = User(
            full_name=full_name, name=name, email=email,
            contact=contact, role=role, is_approved=(role == "trekker"),
        )
        new_user.set_pass_hash(password)
        db.session.add(new_user)
        db.session.commit()

        if role == "trekker":
            flash("Registration successful! Please log in.", "success")
        else:
            flash("Registered! Your staff account is awaiting admin approval.", "info")
        return redirect(url_for("visit.login"))

    return render_template("register.html", form_data={})


@visit.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("visit.home"))
