from flask import Blueprint, request, jsonify, session, render_template
from werkzeug.security import check_password_hash, generate_password_hash
import re
from models import User, db

# IMPORTANT:
# url_prefix='/auth'
# so routes become:
# /auth/login
# /auth/register

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# -------------------------------------------------------------------
# DATABASE HELPERS
# -------------------------------------------------------------------

def get_user_by_email(email: str):
    return User.query.filter_by(email=email).first()


def create_user(first_name, last_name, email, password_hash):
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    return user.id


# -------------------------------------------------------------------
# REGISTER API
# POST -> /auth/register
# -------------------------------------------------------------------

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}

    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    # Validation
    if not first_name or not last_name:
        return jsonify(
            success=False,
            message='First and last name are required.'
        ), 400

    if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify(
            success=False,
            message='A valid email address is required.'
        ), 400

    if len(password) < 8:
        return jsonify(
            success=False,
            message='Password must be at least 8 characters.'
        ), 400

    # Duplicate email
    if get_user_by_email(email):
        return jsonify(
            success=False,
            message='An account with that email already exists.'
        ), 409

    try:
        password_hash = generate_password_hash(password)

        user_id = create_user(
            first_name,
            last_name,
            email,
            password_hash
        )

    except Exception as e:
        print("REGISTER ERROR:", e)

        return jsonify(
            success=False,
            message='Could not create account.'
        ), 500

    # Session
    session['user_id'] = user_id
    session['user_email'] = email

    return jsonify(
        success=True,
        redirect='/dashboard'
    ), 201


# -------------------------------------------------------------------
# LOGIN API
# POST -> /auth/login
# -------------------------------------------------------------------

@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json(silent=True) or {}

    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    remember = bool(data.get('remember', False))

    if not email or not password:
        return jsonify(
            success=False,
            message='Email and password are required.'
        ), 400

    user = get_user_by_email(email)

    if user is None:
        return jsonify(
            success=False,
            message='Invalid email or password.'
        ), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify(
            success=False,
            message='Invalid email or password.'
        ), 401

    session.permanent = remember
    session['user_id'] = user.id
    session['user_email'] = user.email

    return jsonify(
        success=True,
        redirect='/dashboard'
    ), 200


# -------------------------------------------------------------------
# LOGOUT
# POST -> /auth/logout
# -------------------------------------------------------------------

@auth_bp.route('/logout', methods=['POST'])
def logout():

    session.clear()

    return jsonify(
        success=True,
        redirect='/'
    ), 200


# -------------------------------------------------------------------
# CURRENT USER
# GET -> /auth/me
# -------------------------------------------------------------------

@auth_bp.route('/me', methods=['GET'])
def me():

    if 'user_id' not in session:
        return jsonify(authenticated=False), 401

    return jsonify(
        authenticated=True,
        user_id=session['user_id'],
        email=session['user_email']
    ), 200


# -------------------------------------------------------------------
# PAGE ROUTES
# -------------------------------------------------------------------

@auth_bp.route('/login-page')
def login_page():
    return render_template('login.html')


@auth_bp.route('/register-page')
def register_page():
    return render_template('register.html')


@auth_bp.route('/dashboard')
def dashboard():
    return render_template('index.html')