from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Device
from app import db

# ──────────────────────────────────────────────────────
# ✅ Main Blueprint
# 📌 Handles routes for public home page and authenticated dashboard
# ──────────────────────────────────────────────────────
main = Blueprint('main', __name__)

# ──────────────────────────────────────────────────────
# 🏠 Home Route
# URL: /
# Methods: GET
# 📌 Public-facing landing page
# 📤 Renders: home.html (static or marketing info)
# ──────────────────────────────────────────────────────
@main.route('/')
def home():
    return render_template('home.html')

# ──────────────────────────────────────────────────────
# 📊 Dashboard Route
# URL: /dashboard
# Method: GET
# 🔐 Protected: Requires user to be logged in
# 📥 Gets: list of devices owned by current_user from the DB
# 📤 Renders: dashboard.html (with user’s devices)
# ──────────────────────────────────────────────────────
@main.route('/dashboard')
@login_required
def dashboard():
    # Query all devices linked to the current logged-in user
    devices = Device.query.filter_by(user_id=current_user.id).all()
    
    # Pass the device list to the dashboard template
    return render_template('dashboard.html', devices=devices)
