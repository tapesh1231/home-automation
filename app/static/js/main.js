document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed.');

    // ================= Handle Save Device Button =================
    document.getElementById('saveDevice').addEventListener('click', function () {
        console.log('Save Device button clicked.');

        const name = document.getElementById('deviceName').value;
        const type = document.getElementById('deviceType').value;
        const deviceId = document.getElementById('deviceId').value;
        const secretKey = document.getElementById('deviceSecret').value;

        // Validate input fields
        if (!name || !type || !deviceId || !secretKey) {
            showToast('All fields are required!', 'danger');
            return;
        }

        // Send POST request to add the device
        fetch('/api/v1/device/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                type: type,
                device_id: deviceId,
                secret_key: secretKey
            })
        })
            .then(response => {
                console.log('Add device response:', response);
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                console.log('Device added successfully:', data);
                showToast('Device added successfully!', 'success');
                bootstrap.Modal.getInstance(document.getElementById('addDeviceModal')).hide();
                document.getElementById('addDeviceForm').reset();

                // Optionally, dynamically update the UI with the new device
                const devicesContainer = document.getElementById('devices-container');
                const newDeviceHTML = `
                    <div class="col-md-6 mb-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">${data.name} (${data.device_id})</h5>
                                <p class="card-text">
                                    Type: ${data.type}<br>
                                    Last Updated: Never
                                </p>
                            </div>
                        </div>
                    </div>`;
                devicesContainer.insertAdjacentHTML('beforeend', newDeviceHTML);
            })
            .catch(error => {
                console.error('Error adding device:', error);
                showToast(error.error || 'Failed to add device', 'danger');
            });
    });

    // ================= Handle Relay Toggles =================
    // ================= Handle Relay Toggles =================
document.querySelectorAll('.relay-toggle').forEach(toggle => {
    toggle.addEventListener('change', function() {
        const deviceId = this.dataset.deviceId;
        const relayNum = this.dataset.relay;
        const newState = this.checked;

        console.log(`Toggling relay - Device: ${deviceId}, Relay: ${relayNum}, State: ${newState}`);

        // Send update to server
        fetch(`/api/v1/device/control/${deviceId}/${relayNum}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                state: newState
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update relay state');
            }
            return response.json();
        })
        .then(data => {
            console.log('Relay state updated:', data);
            // Update UI to reflect new state
            const statusElement = document.querySelector(
                `.relay-status[data-device-id="${deviceId}"][data-relay="${relayNum}"]`
            );
            if (statusElement) {
                statusElement.textContent = newState ? 'ON' : 'OFF';
            }
        })
        .catch(error => {
            console.error('Error updating relay:', error);
            // Revert toggle if update failed
            this.checked = !newState;
            showToast('Failed to update relay state', 'danger');
        });
    });
});

    // ================= Toast Notification Function =================
    function showToast(message, type = 'success') {
        console.log(`Showing toast: ${message}, Type: ${type}`);

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        const toastContainer = document.getElementById('toastContainer') || createToastContainer();
        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', function () {
            console.log('Toast hidden:', toast);
            toast.remove();
        });
    }

    function createToastContainer() {
        console.log('Creating toast container if not exists.');

        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '1100';
            document.body.appendChild(container);
        }
        return container;
    }

    // ================= Periodic Device State Refresh =================
    setInterval(() => {
        console.log('Refreshing device states...');

        fetch('/api/v1/devices')
            .then(response => {
                console.log('Fetch devices response:', response);
                if (!response.ok) {
                    throw new Error(`Failed to fetch devices. Status: ${response.status}`);
                }
                return response.json();
            })
            .then(devices => {
                console.log('Fetched devices:', devices);

                devices.forEach(device => {
                    console.log('Processing device:', device);

                    for (let i = 1; i <= 8; i++) {
                        const relayKey = `relay_${i}`;
                        const toggle = document.querySelector(
                            `.relay-toggle[data-device-id="${device.device_id}"][data-relay="${i}"]`
                        );
                        const status = document.querySelector(
                            `.relay-status[data-device-id="${device.device_id}"][data-relay="${i}"]`
                        );

                        if (toggle && status) {
                            const newState = device.relay_states?.[relayKey];
                            console.log(`Relay ${i} state for device ${device.device_id}:`, newState);

                            if (newState !== undefined) {
                                toggle.checked = newState;
                                status.textContent = newState ? 'ON' : 'OFF';
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error refreshing states:', error);
            });
    }, 10000); // Every 10 seconds
});