from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    devices = db.relationship('Device', backref='owner', lazy=True)

# class Device(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     device_type = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.Boolean, default=False)
#     last_updated = db.Column(db.DateTime, default=datetime.utcnow)
#     device_id = db.Column(db.String(20), unique=True, nullable=False)

#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    device_id = db.Column(db.String(32), unique=True, nullable=False)  # e.g. "AP001"
    secret_key = db.Column(db.String(128), nullable=False)  # Hashed secret
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    relay_states = db.Column(db.JSON, default={
        'relay_1': False,
        'relay_2': False,
        'relay_3': False,
        'relay_4': False,
        'relay_5': False,
        'relay_6': False,
        'relay_7': False,
        'relay_8': False
    })
    
   # user = db.relationship('User', backref='devices')