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


# --ADMIN-- routes
@visit.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    total_treks = Treks.query.count()
    total_users = User.query.filter_by(role="trekker").count()
    total_staff = User.query.filter_by(role="staff").count()
    total_bookings = Bookings.query.count()
    pending_staff = User.query.filter_by(role="staff", is_approved=False).count()
    recent_bookings = Bookings.query.order_by(Bookings.booked_at.desc()).limit(5).all()

    trek_stats = db.session.query(Treks.difficulty, db.func.count(Treks.id)).group_by(Treks.difficulty).all()
    status_stats = db.session.query(Treks.status, db.func.count(Treks.id)).group_by(Treks.status).all()

    return render_template(
        "admin/dashboard.html", total_treks=total_treks, total_users=total_users,
        total_staff=total_staff, total_bookings=total_bookings, pending_staff=pending_staff,
        recent_bookings=recent_bookings, trek_stats=trek_stats, status_stats=status_stats,
    )


@visit.route("/admin/treks")
@login_required
@admin_required
def admin_treks():
    q = request.args.get("q", "")
    difficulty = request.args.get("difficulty", "")
    status = request.args.get("status", "")

    query = Treks.query
    if q:
        query = query.filter(db.or_(Treks.name.ilike(f"%{q}%"), Treks.location.ilike(f"%{q}%")))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if status:
        query = query.filter_by(status=status)
    treks = query.order_by(Treks.created_at.desc()).all()

    return render_template(
        "admin/treks.html", treks=treks, query=q, difficulty=difficulty, status=status,
        difficulties=DIFFICULTIES, statuses=TREK_STATUSES,
    )


def _trek_from_form(trek):
    f = request.form
    trek.name = f.get("name", "").strip()
    trek.location = f.get("location", "").strip()
    trek.description = f.get("description", "").strip()
    trek.difficulty = f.get("difficulty", "Easy")
    trek.capacity = int(f.get("capacity") or 1)
    trek.available = int(f.get("available") or trek.capacity)
    trek.price = float(f.get("price") or 0)
    trek.altitude = f.get("altitude", "").strip()
    trek.image_url = f.get("image_url", "").strip()
    trek.highlights = f.get("highlights", "").strip()
    trek.requirements = f.get("requirements", "").strip()
    start = f.get("starting_date") or None
    end = f.get("ending_date") or None
    trek.starting_date = datetime.strptime(start, "%Y-%m-%d").date() if start else trek.starting_date
    trek.ending_date = datetime.strptime(end, "%Y-%m-%d").date() if end else trek.ending_date
    if trek.starting_date and trek.ending_date:
        delta = (trek.ending_date - trek.starting_date).days + 1
        trek.duration = max(1, delta)


@visit.route("/admin/treks/new", methods=["GET", "POST"])
@login_required
@admin_required
def admin_new_trek():
    if request.method == "POST":
        trek = Treks(status="Pending")
        _trek_from_form(trek)
        db.session.add(trek)
        db.session.commit()
        flash("Trek created!", "success")
        return redirect(url_for("visit.admin_treks"))
    return render_template("admin/trek_form.html", trek=None, title="New Trek",difficulties=DIFFICULTIES)


@visit.route("/admin/treks/<int:trek_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_trek(trek_id):
    trek = Treks.query.get_or_404(trek_id)
    if request.method == "POST":
        _trek_from_form(trek)
        db.session.commit()
        flash("Trek updated!", "success")
        return redirect(url_for("visit.admin_treks"))
    return render_template("admin/trek_form.html", trek=trek, title="Edit Trek",difficulties=DIFFICULTIES)


@visit.route("/admin/treks/<int:trek_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_trek(trek_id):
    trek = Treks.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash("Trek deleted.", "success")
    return redirect(url_for("visit.admin_treks"))


@visit.route("/admin/treks/<int:trek_id>/approve", methods=["POST"])
@login_required
@admin_required
def admin_approve_trek(trek_id):
    trek = Treks.query.get_or_404(trek_id)
    trek.status = "Approved"
    db.session.commit()
    flash("Trek approved!", "success")
    return redirect(url_for("visit.admin_treks"))


@visit.route("/admin/treks/<int:trek_id>/setstatus", methods=["POST"])
@login_required
@admin_required
def admin_set_trek_status(trek_id):
    status = request.form.get("status")
    if status in TREK_STATUSES:
        trek = Treks.query.get_or_404(trek_id)
        trek.status = status
        if status == "Completed":
            Bookings.query.filter_by(trek_id=trek.id, status="Booked").update({"status": "Completed"})
        db.session.commit()
        flash(f"Status set to {status}.", "success")
    return redirect(url_for("visit.admin_treks"))


@visit.route("/admin/treks/<int:trek_id>/assign", methods=["GET", "POST"])
@login_required
@admin_required
def admin_assign_staff(trek_id):
    trek = Treks.query.get_or_404(trek_id)
    if request.method == "POST":
        staff_id = request.form.get("staff_id")
        trek.assigned_staff_id = int(staff_id) if staff_id and staff_id != "0" else None
        db.session.commit()
        flash("Staff assigned!", "success")
        return redirect(url_for("visit.admin_treks"))
    approved_staff = User.query.filter_by(role="staff", is_approved=True, is_blacklisted=False).all()
    return render_template("admin/assign_staff.html", trek=trek, approved_staff=approved_staff)


@visit.route("/admin/staff")
@login_required
@admin_required
def admin_staff_list():
    q = request.args.get("q", "")
    query = User.query.filter_by(role="staff")
    if q:
        query = query.filter(db.or_(User.name.ilike(f"%{q}%"), User.full_name.ilike(f"%{q}%")))
    staff = query.order_by(User.created_at.desc()).all()
    return render_template("admin/staff_list.html", staff=staff, query=q)


@visit.route("/admin/staff/<int:user_id>/approve", methods=["POST"])
@login_required
@admin_required
def admin_approve_staff(user_id):
    staff = User.query.filter_by(id=user_id, role="staff").first_or_404()
    staff.is_approved = True
    db.session.commit()
    flash("Staff approved!", "success")
    return redirect(url_for("visit.admin_staff_list"))


@visit.route("/admin/staff/<int:user_id>/reject", methods=["POST"])
@login_required
@admin_required
def admin_reject_staff(user_id):
    staff = User.query.filter_by(id=user_id, role="staff").first_or_404()
    db.session.delete(staff)
    db.session.commit()
    flash("Staff registration rejected.", "info")
    return redirect(url_for("visit.admin_staff_list"))


@visit.route("/admin/users")
@login_required
@admin_required
def admin_users():
    q = request.args.get("q", "")
    query = User.query.filter_by(role="trekker")
    if q:
        query = query.filter(db.or_(User.name.ilike(f"%{q}%"), User.full_name.ilike(f"%{q}%")))
    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users, query=q)


@visit.route("/admin/users/<int:user_id>/blacklist", methods=["POST"])
@login_required
@admin_required
def admin_blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    flash(f"User {'blacklisted' if user.is_blacklisted else 'reinstated'}.", "success")
    return redirect(request.referrer or url_for("visit.admin_users"))


@visit.route("/admin/bookings")
@login_required
@admin_required
def admin_bookings():
    bookings = Bookings.query.order_by(Bookings.booked_at.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings)


# --Staff-- routes
@visit.route("/staff/dashboard")
@login_required
@staff_required
def staff_dashboard():
    assigned_treks = Treks.query.filter_by(assigned_staff_id=session["user_id"]).all()
    trek_ids = [t.id for t in assigned_treks]
    total_participants = 0
    if trek_ids:
        total_participants = Bookings.query.filter(
            Bookings.trek_id.in_(trek_ids), Bookings.status == "Booked"
        ).count()
    return render_template("staff/dashboard.html", assigned_treks=assigned_treks,
                            total_participants=total_participants)


@visit.route("/staff/trek/<int:trek_id>")
@login_required
@staff_required
def staff_trek_detail(trek_id):
    trek = Treks.query.get_or_404(trek_id)
    if trek.assigned_staff_id != session["user_id"] and session.get("role") != "admin":
        abort(403)
    bookings = Bookings.query.filter_by(trek_id=trek_id, status="Booked").all()
    return render_template("staff/trek_detail.html", trek=trek, bookings=bookings)


@visit.route("/staff/trek/<int:trek_id>/update", methods=["POST"])
@login_required
@staff_required
def staff_update_trek(trek_id):
    trek = Treks.query.get_or_404(trek_id)
    if trek.assigned_staff_id != session["user_id"]:
        abort(403)
    trek.available = int(request.form.get("available", 0))
    status = request.form.get("status", "Open")
    trek.status = status if status in TREK_STATUSES else "Open"
    if trek.status == "Completed":
        Bookings.query.filter_by(trek_id=trek.id, status="Booked").update({"status": "Completed"})
    db.session.commit()
    flash("Trek updated!", "success")
    return redirect(url_for("visit.staff_trek_detail", trek_id=trek_id))


# --User-- routes
@visit.route("/user/dashboard")
@login_required
def user_dashboard():
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("visit.admin_dashboard"))
    if role == "staff":
        return redirect(url_for("visit.staff_dashboard"))

    uid = session["user_id"]
    open_treks = Treks.query.filter_by(status="Open").order_by(Treks.starting_date).limit(4).all()
    my_bookings = Bookings.query.filter_by(user_id=uid).order_by(Bookings.booked_at.desc()).limit(5).all()
    total_booked = Bookings.query.filter_by(user_id=uid, status="Booked").count()
    total_completed = Bookings.query.filter_by(user_id=uid, status="Completed").count()
    return render_template(
        "user/dashboard.html", open_treks=open_treks, my_bookings=my_bookings,
        total_booked=total_booked, total_completed=total_completed,
    )


@visit.route("/user/treks")
@login_required
def browse_treks():
    q = request.args.get("q", "")
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")

    query = Treks.query.filter_by(status="Open")
    if q:
        query = query.filter(db.or_(Treks.name.ilike(f"%{q}%"), Treks.location.ilike(f"%{q}%")))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Treks.location.ilike(f"%{location}%"))
    treks = query.order_by(Treks.starting_date).all()

    return render_template("user/browse_treks.html", treks=treks, query=q,
                            difficulty=difficulty, location=location, difficulties=DIFFICULTIES)


@visit.route("/user/treks/<int:trek_id>")
@login_required
def trek_detail(trek_id):
    trek = Treks.query.get_or_404(trek_id)
    already_booked = Bookings.query.filter_by(
        user_id=session["user_id"], trek_id=trek_id, status="Booked"
    ).first()
    return render_template("user/trek_detail.html", trek=trek, already_booked=already_booked)


@visit.route("/user/treks/<int:trek_id>/book", methods=["POST"])
@login_required
@active_required
def book_trek(trek_id):
    if session.get("role") != "trekker":
        flash("Only trekkers can book treks.", "danger")
        return redirect(url_for("visit.trek_detail", trek_id=trek_id))

    trek = Treks.query.get_or_404(trek_id)
    if trek.status != "Open":
        flash("This trek is not open for booking.", "danger")
        return redirect(url_for("visit.trek_detail", trek_id=trek_id))

    uid = session["user_id"]
    if Bookings.query.filter_by(user_id=uid, trek_id=trek_id, status="Booked").first():
        flash("You have already booked this trek!", "warning")
        return redirect(url_for("visit.trek_detail", trek_id=trek_id))

    participants = max(1, int(request.form.get("participants", 1)))
    if trek.available < participants:
        flash(f"Only {trek.available} slots left.", "danger")
        return redirect(url_for("visit.trek_detail", trek_id=trek_id))

    contact = request.form.get("emergency_contact", "").strip()
    phone = request.form.get("emergency_phone", "").strip()
    if not contact or not phone:
        flash("Emergency contact details are required.", "danger")
        return redirect(url_for("visit.trek_detail", trek_id=trek_id))

    booking = Bookings(
        user_id=uid, trek_id=trek_id, participants=participants,
        emergency_contact=contact, emergency_phone=phone,
        notes=request.form.get("special_requirements", "").strip(),
        status="Booked",
    )
    db.session.add(booking)
    trek.available -= participants
    if trek.available == 0:
        trek.status = "Closed"
    db.session.commit()
    flash("Trek booked! Have a great trip.", "success")
    return redirect(url_for("visit.my_bookings"))


@visit.route("/user/bookings")
@login_required
def my_bookings():
    bookings = Bookings.query.filter_by(user_id=session["user_id"]).order_by(Bookings.booked_at.desc()).all()
    return render_template("user/my_bookings.html", bookings=bookings)


@visit.route("/user/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    booking = Bookings.query.filter_by(id=booking_id, user_id=session["user_id"]).first_or_404()
    if booking.status != "Booked":
        flash("This booking can no longer be cancelled.", "warning")
        return redirect(url_for("visit.my_bookings"))

    booking.status = "Cancelled"
    trek = booking.trek
    if trek:
        trek.available += booking.participants
        if trek.status == "Closed" and trek.available > 0:
            trek.status = "Open"
    db.session.commit()
    flash("Booking cancelled.", "info")
    return redirect(url_for("visit.my_bookings"))


@visit.route("/user/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get_or_404(session["user_id"])
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        contact = request.form.get("contact", "").strip()
        address = request.form.get("address", "").strip()
        bio = request.form.get("bio", "").strip()

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not email or "@" not in email:
            errors.append("A valid email is required.")
        if User.query.filter(User.email == email, User.id != user.id).first():
            errors.append("That email is already in use.")

        if errors:
            for e in errors:
                flash(e, "danger")
        else:
            user.full_name = full_name
            user.email = email
            user.contact = contact
            user.address = address
            user.bio = bio
            db.session.commit()
            load_session(user)
            flash("Profile updated!", "success")
        return redirect(url_for("visit.profile"))

    return render_template("user/profile.html", user=user)