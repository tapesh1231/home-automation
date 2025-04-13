from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

# ──────────────────────────────────────────────────────
# ✅ Authentication Blueprint
# 📌 Handles login, registration, and logout functionality
# 📥 Gets user input via forms
# 📤 Sends user to dashboard/home views after login or logout
# ──────────────────────────────────────────────────────
auth = Blueprint('auth', __name__)

# ──────────────────────────────────────────────────────
# 🔐 Login Route
# URL: /login
# Methods: GET (to display form), POST (to submit login data)
# 📥 Gets data: from login form (email, password, remember)
# 📤 Redirects: to dashboard on success, or back to login on error
# ──────────────────────────────────────────────────────
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Already logged in, go to dashboard
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Fetch user from DB using email
        user = User.query.filter_by(email=email).first()
        
        # Verify password
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))

        # Valid login → create session
        login_user(user, remember=remember)
        return redirect(url_for('main.dashboard'))
    
    # GET request → show login form
    return render_template('login.html')

# ──────────────────────────────────────────────────────
# 🧾 Registration Route
# URL: /register
# Methods: GET (show form), POST (create new user)
# 📥 Gets data: from form (email, username, password)
# 📤 Sends: confirmation message and redirects to login
# ──────────────────────────────────────────────────────
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # Already logged in, go to dashboard
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.register'))

        # Create new user with hashed password
        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )

        # Save user to DB
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    # GET request → show register form
    return render_template('register.html')

# ──────────────────────────────────────────────────────
# 🚪 Logout Route
# URL: /logout
# Method: GET
# 📌 Logs out user and clears session
# 📤 Redirects to home page
# ──────────────────────────────────────────────────────
@auth.route('/logout')
def logout():
    logout_user()  # Removes user from session
    return redirect(url_for('main.home'))
