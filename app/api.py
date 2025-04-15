# from flask import Blueprint, jsonify, request
# from flask_login import login_required, current_user
# from app.models import Device, db
# from datetime import datetime

# # Create a blueprint for API routes
# api = Blueprint('api', __name__)

# # ───────────────────────────────────────────────────────────────────────
# # ✅ ROUTE: GET /api/devices
# # 📌 Purpose: Fetch all devices belonging to the logged-in user
# # 📥 Gets data: From the database (Device model, filtered by user_id)
# # 📤 Sends data: To the frontend dashboard (usually for listing user's devices)
# # ───────────────────────────────────────────────────────────────────────
# @api.route('/devices', methods=['GET'])
# @login_required
# def get_devices():
#     devices = Device.query.filter_by(user_id=current_user.id).all()
#     return jsonify([{
#         'id': device.id,
#         'name': device.name,
#         'type': device.device_type,
#         'status': device.status,
#         'last_updated': device.last_updated
#     } for device in devices])


# # ───────────────────────────────────────────────────────────────────────
# # ✅ ROUTE: GET/POST /api/device/<int:device_id>
# # 📌 Purpose:
# #   - GET: Get current status of a specific device
# #   - POST: Update the status of a specific device (on/off)
# # 📥 Gets data: From the database (Device by id) and from request (POST JSON)
# # 📤 Sends data: To the frontend device control panel
# # ───────────────────────────────────────────────────────────────────────
# @api.route('/device/<int:device_id>', methods=['GET', 'POST'])
# @login_required
# def control_device(device_id):
#     device = Device.query.filter_by(id=device_id, user_id=current_user.id).first_or_404()
    
#     if request.method == 'POST':
#         data = request.get_json()
#         if 'status' in data:
#             device.status = data['status']
#             device.last_updated = datetime.utcnow()
#             db.session.commit()
            
#         return jsonify({
#             'id': device.id,
#             'name': device.name,
#             'type': device.device_type,
#             'status': device.status,
#             'last_updated': device.last_updated
#         })
    
#     return jsonify({
#         'id': device.id,
#         'name': device.name,
#         'type': device.device_type,
#         'status': device.status,
#         'last_updated': device.last_updated
#     })


# # ───────────────────────────────────────────────────────────────────────
# # ✅ ROUTE: POST /api/device/add
# # 📌 Purpose: Add/register a new device for the logged-in user
# # 📥 Gets data: From the frontend form (JSON with name, type, and device_id)
# # 📤 Sends data: Confirmation to the frontend that the device was added
# # ───────────────────────────────────────────────────────────────────────
# @api.route('/device/add', methods=['POST'])
# @login_required
# def add_device():
#     data = request.get_json()

#     # Check for required fields
#     if 'name' not in data or 'type' not in data or 'device_id' not in data:
#         return jsonify({'error': 'Missing required fields'}), 400
    
#     # Prevent duplicate device_id
#     existing = Device.query.filter_by(device_id=data['device_id']).first()
#     if existing:
#         return jsonify({'error': 'Device ID already exists'}), 400
    
#     new_device = Device(
#         name=data['name'],
#         device_type=data['type'],
#         status=False,
#         user_id=current_user.id,
#         device_id=data['device_id']
#     )
    
#     db.session.add(new_device)
#     db.session.commit()
    
#     return jsonify({
#         'id': new_device.id,
#         'name': new_device.name,
#         'type': new_device.device_type,
#         'status': new_device.status,
#         'message': 'Device added successfully'
#     }), 201


# # ───────────────────────────────────────────────────────────────────────
# # ✅ ROUTE: GET /api/device/control/<string:device_id>
# # 📌 Purpose: ESP device fetches its current state from the server
# # 📥 Gets data: From the database using device_id (not user ID)
# # 📤 Sends data: To the ESP/IoT device (to know whether to turn ON/OFF)
# # ───────────────────────────────────────────────────────────────────────
# @api.route('/device/control/<string:device_id>', methods=['GET'])
# def get_device_state_by_code(device_id):
#     device = Device.query.filter_by(device_id=device_id).first()
    
#     if not device:
#         return jsonify({'error': 'Device not found'}), 404
    
#     return jsonify({
#         'id': device.id,
#         'name': device.name,
#         'type': device.device_type,
#         'status': device.status,
#         'last_updated': device.last_updated
#     })

from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from app.models import Device, db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint('api', __name__)

# Helper function for device authentication
def authenticate_device(device_id, secret_key=None):
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        abort(404, description="Device not found")
    
    if secret_key:
        if not check_password_hash(device.secret_key, secret_key):
            abort(403, description="Invalid credentials")
    
    return device

@api.route('/devices', methods=['GET'])
@login_required
def get_devices():
    devices = Device.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'device_id': device.device_id,
        'name': device.name,
        'type': device.device_type,
        'relay_states': device.relay_states,
        'last_updated': device.last_updated
    } for device in devices])

# @api.route('/device/state/<string:device_id>', methods=['GET', 'POST'])
# def device_state(device_id):
    if request.method == 'GET':
        # ESP8266 fetching current state
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            abort(401, description="Missing authorization")
        
        secret_key = auth_header.split(' ')[1]
        device = authenticate_device(device_id, secret_key)
        
        return jsonify({
            device.device_id: device.relay_states
        })
    
    elif request.method == 'POST':
        # ESP8266 sending state updates
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            abort(401, description="Missing authorization")
        
        secret_key = auth_header.split(' ')[1]
        device = authenticate_device(device_id, secret_key)
        
        data = request.get_json()
        device_data = data.get(device_id, {})
        
        # Update only the relays that were sent
        for relay, state in device_data.items():
            if relay in device.relay_states:
                device.relay_states[relay] = state
        
        device.last_updated = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "State updated",
            device.device_id: device.relay_states
        })


@api.route('/device/state/<string:device_id>', methods=['GET', 'POST'])
def device_state(device_id):
    # Handle GET request for device state
    if request.method == 'GET':
        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            abort(401, description="Authorization header missing")
        if not auth_header.startswith('Bearer '):
            abort(401, description="Authorization must be in 'Bearer <token>' format")
        
        secret_key = auth_header.split(' ')[1]
        device = authenticate_device(device_id, secret_key)

        # Debugging: Print the device's relay states
        print(f"Device {device.device_id} relay states: {device.relay_states}")
        
        return jsonify({
            device.device_id: device.relay_states
        })
    
    # Handle POST request for updating device state
    elif request.method == 'POST':
        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            abort(401, description="Authorization header missing")
        if not auth_header.startswith('Bearer '):
            abort(401, description="Authorization must be in 'Bearer <token>' format")
        
        secret_key = auth_header.split(' ')[1]
        device = authenticate_device(device_id, secret_key)

        data = request.get_json()

        # Debugging: Print incoming data
        print(f"Incoming data for device {device_id}: {data}")
        
        if not isinstance(data, dict):
            abort(400, description="Invalid JSON data format")
        
        device_data = data.get(device_id, {})
        
        # Debugging: Print the relay states being updated
        print(f"Device data for {device_id}: {device_data}")
        
        if not isinstance(device_data, dict):
            abort(400, description="Invalid data format for relay states")

        # Update only the relays that were sent
        for relay, state in device_data.items():
            if relay in device.relay_states:
                device.relay_states[relay] = state
                # Debugging: Print updated relay state
                print(f"Updated {relay} to {state}")
            else:
                abort(400, description=f"Invalid relay name {relay}")
        
        device.last_updated = datetime.utcnow()
        db.session.commit()

        # Debugging: Print the updated relay states after commit
        print(f"Updated relay states for device {device.device_id}: {device.relay_states}")
        
        return jsonify({
            "message": "State updated",
            device.device_id: device.relay_states
        })



@api.route('/device/control/<string:device_id>/<int:relay_num>', methods=['POST'])
@login_required
def control_relay(device_id, relay_num):
    try:
        if relay_num < 1 or relay_num > 8:
            abort(400, description="Relay number must be between 1 and 8")
        
        # Get device with fresh session
        device = Device.query.filter_by(device_id=device_id, user_id=current_user.id).first_or_404()
        
        data = request.get_json()
        if 'state' not in data:
            abort(400, description="Missing state parameter")
        
        relay_key = f'relay_{relay_num}'
        new_state = bool(data['state'])
        
        # Make a deep copy of current states to force change detection
        new_states = dict(device.relay_states)
        new_states[relay_key] = new_state
        
        # Explicitly mark as modified
        from sqlalchemy.orm.attributes import flag_modified
        device.relay_states = new_states
        flag_modified(device, "relay_states")
        
        device.last_updated = datetime.utcnow()
        db.session.commit()
        
        # Refresh the object to verify
        db.session.refresh(device)
        print(f"Verified states after refresh: {device.relay_states}")
        
        return jsonify({
            "message": f"Relay {relay_num} state updated",
            "device_id": device.device_id,
            "relay": relay_key,
            "state": new_state
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating relay: {str(e)}")
        abort(500, description="Failed to update relay state")

@api.route('/device/add', methods=['POST'])
@login_required
def add_device():
    data = request.get_json()

    # Check for required fields
    required_fields = ['name', 'type', 'device_id', 'secret_key']
    print('required_fields', required_fields)
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Prevent duplicate device_id
    if Device.query.filter_by(device_id=data['device_id']).first():
        print('Device ID already exists')
        return jsonify({'error': 'Device ID already exists'}), 400
    
    print(f"name: {len(data['name'])}")
    print(f"type: {len(data['type'])}")
    print(f"device_id: {len(data['device_id'])}")
    print(f"secret_key: {len(data['secret_key'])}")
    
    new_device = Device(
        name=data['name'],
        device_type=data['type'],
        device_id=data['device_id'],
        secret_key=generate_password_hash(data['secret_key']),
        user_id=current_user.id,
       

        
        relay_states={
            'relay_1': False,
            'relay_2': False,
            'relay_3': False,
            'relay_4': False,
            'relay_5': False,
            'relay_6': False,
            'relay_7': False,
            'relay_8': False
         
        }
    )
       
    print('new_device relay states', new_device.relay_states)
    print('new_device outside relay', new_device)


    
    db.session.add(new_device)
    db.session.commit()
    
    return jsonify({
        'device_id': new_device.device_id,
        'name': new_device.name,
        'type': new_device.device_type,
        'message': 'Device added successfully'
    }), 201