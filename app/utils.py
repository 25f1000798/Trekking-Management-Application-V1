from functools import wraps
from flask import session, redirect, url_for, flash, abort

class AnonUser:
    is_authenticated = False
    role = None
    id = None

class SessionUser:

    def __init__(self, s):
        self.is_authenticated = True
        self.id = s.get('user_id')
        self.name = s.get('name')
        self.full_name = s.get('full_name')
        self.role = s.get('role')
        self.email = s.get('email')
        self.contact = s.get('contact')
        self.address = s.get('address')
        self.bio = s.get('bio')
        self.is_blacklisted = s.get('is_blacklisted', False)
        self.is_approved = s.get('is_approved', True)


def current_user():
    if 'user_id' not in session:
        return AnonUser()
    return SessionUser(session)


def load_session(user):
    session.permanent = True
    session['user_id'] = user.id
    session['name'] = user.name
    session['full_name'] = user.full_name
    session['role'] = user.role
    session['email'] = user.email
    session['contact'] = user.contact
    session['address'] = user.address
    session['bio'] = user.bio
    session['is_blacklisted'] = user.is_blacklisted
    session['is_approved'] = user.is_approved


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'info')
            return redirect(url_for('visit.login'))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def staff_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('visit.login'))
        role = session.get('role')
        if role not in ('staff', 'admin'):
            abort(403)
        if role == 'staff' and not session.get('is_approved'):
            flash('Your staff account is pending admin approval.', 'warning')
            return redirect(url_for('visit.home'))
        return f(*args, **kwargs)
    return wrapper


def active_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('visit.login'))
        if session.get('is_blacklisted'):
            flash('Your account has been blacklisted. Contact admin.', 'danger')
            return redirect(url_for('visit.login'))
        return f(*args, **kwargs)
    return wrapper


def difficulty_color(difficulty):
    return {'Easy': 'success', 'Moderate': 'warning', 'Hard': 'danger'}.get(difficulty, 'secondary')


def status_color(status):
    return {
        'Pending': 'secondary', 'Approved': 'info',
        'Open': 'success', 'Closed': 'warning',
        'Completed': 'primary', 'Booked': 'success',
        'Cancelled': 'danger',
    }.get(status, 'secondary')


def format_date(value):
    if not value:
        return '—'
    return value.strftime('%d %b %Y')


def format_duration(days):
    if not days or days < 1:
        return '—'
    weeks, remainder = divmod(int(days), 7)
    parts = []
    if weeks:
        parts.append(f"{weeks} Week{'s' if weeks > 1 else ''}")
    if remainder:
        parts.append(f"{remainder} Day{'s' if remainder > 1 else ''}")
    return ' '.join(parts) if parts else f"{days} Day{'s' if days != 1 else ''}"
