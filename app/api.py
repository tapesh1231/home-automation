from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Device, db
from datetime import datetime

# Create a blueprint for API routes
api = Blueprint('api', __name__)

# ───────────────────────────────────────────────────────────────────────
# ✅ ROUTE: GET /api/devices
# 📌 Purpose: Fetch all devices belonging to the logged-in user
# 📥 Gets data: From the database (Device model, filtered by user_id)
# 📤 Sends data: To the frontend dashboard (usually for listing user's devices)
# ───────────────────────────────────────────────────────────────────────
@api.route('/devices', methods=['GET'])
@login_required
def get_devices():
    devices = Device.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': device.id,
        'name': device.name,
        'type': device.device_type,
        'status': device.status,
        'last_updated': device.last_updated
    } for device in devices])


# ───────────────────────────────────────────────────────────────────────
# ✅ ROUTE: GET/POST /api/device/<int:device_id>
# 📌 Purpose:
#   - GET: Get current status of a specific device
#   - POST: Update the status of a specific device (on/off)
# 📥 Gets data: From the database (Device by id) and from request (POST JSON)
# 📤 Sends data: To the frontend device control panel
# ───────────────────────────────────────────────────────────────────────
@api.route('/device/<int:device_id>', methods=['GET', 'POST'])
@login_required
def control_device(device_id):
    device = Device.query.filter_by(id=device_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        data = request.get_json()
        if 'status' in data:
            device.status = data['status']
            device.last_updated = datetime.utcnow()
            db.session.commit()
            
        return jsonify({
            'id': device.id,
            'name': device.name,
            'type': device.device_type,
            'status': device.status,
            'last_updated': device.last_updated
        })
    
    return jsonify({
        'id': device.id,
        'name': device.name,
        'type': device.device_type,
        'status': device.status,
        'last_updated': device.last_updated
    })


# ───────────────────────────────────────────────────────────────────────
# ✅ ROUTE: POST /api/device/add
# 📌 Purpose: Add/register a new device for the logged-in user
# 📥 Gets data: From the frontend form (JSON with name, type, and device_id)
# 📤 Sends data: Confirmation to the frontend that the device was added
# ───────────────────────────────────────────────────────────────────────
@api.route('/device/add', methods=['POST'])
@login_required
def add_device():
    data = request.get_json()

    # Check for required fields
    if 'name' not in data or 'type' not in data or 'device_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Prevent duplicate device_id
    existing = Device.query.filter_by(device_id=data['device_id']).first()
    if existing:
        return jsonify({'error': 'Device ID already exists'}), 400
    
    new_device = Device(
        name=data['name'],
        device_type=data['type'],
        status=False,
        user_id=current_user.id,
        device_id=data['device_id']
    )
    
    db.session.add(new_device)
    db.session.commit()
    
    return jsonify({
        'id': new_device.id,
        'name': new_device.name,
        'type': new_device.device_type,
        'status': new_device.status,
        'message': 'Device added successfully'
    }), 201


# ───────────────────────────────────────────────────────────────────────
# ✅ ROUTE: GET /api/device/control/<string:device_id>
# 📌 Purpose: ESP device fetches its current state from the server
# 📥 Gets data: From the database using device_id (not user ID)
# 📤 Sends data: To the ESP/IoT device (to know whether to turn ON/OFF)
# ───────────────────────────────────────────────────────────────────────
@api.route('/device/control/<string:device_id>', methods=['GET'])
def get_device_state_by_code(device_id):
    device = Device.query.filter_by(device_id=device_id).first()
    
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    return jsonify({
        'id': device.id,
        'name': device.name,
        'type': device.device_type,
        'status': device.status,
        'last_updated': device.last_updated
    })
