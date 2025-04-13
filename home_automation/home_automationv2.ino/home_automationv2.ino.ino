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

@api.route('/device/state/<string:device_id>', methods=['GET', 'POST'])
def device_state(device_id):
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

@api.route('/device/control/<string:device_id>/<int:relay_num>', methods=['POST'])
@login_required
def control_relay(device_id, relay_num):
    if relay_num < 1 or relay_num > 8:
        abort(400, description="Relay number must be between 1 and 8")
    
    device = Device.query.filter_by(device_id=device_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    
    if 'state' not in data:
        abort(400, description="Missing state parameter")
    
    relay_key = f'relay_{relay_num}'
    new_state = bool(data['state'])
    
    # Update the specific relay state
    device.relay_states[relay_key] = new_state
    device.last_updated = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        "message": f"Relay {relay_num} state updated",
        "device_id": device.device_id,
        "relay": relay_key,
        "state": new_state
    })

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
    ), 201