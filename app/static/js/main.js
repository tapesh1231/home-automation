// dashboard.js

document.addEventListener('DOMContentLoaded', function () {

    // ================= Device Toggle =====================
    // Handles the toggle switch for each device.
    // Sends POST request to update the device status (On/Off)
    document.querySelectorAll('.device-toggle').forEach(toggle => {
        toggle.addEventListener('change', function () {
            const deviceId = this.dataset.id;
            const newStatus = this.checked;

            // Send updated status to the server
            fetch(`/api/device/${deviceId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus })
            })
                .then(response => response.json())
                .then(data => {
                    // Update the UI with new status
                    document.querySelector(`.device-status[data-id="${deviceId}"]`).textContent =
                        data.status ? 'On' : 'Off';
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.checked = !newStatus; // Revert toggle if request fails
                });
        });
    });

    // ================= Add New Device =====================
    // Handles the "Save Device" button click
    // Sends POST request to add a new device to the backend
    document.getElementById('saveDevice').addEventListener('click', function () {
        const name = document.getElementById('deviceName').value;
        const type = document.getElementById('deviceType').value;
        const device_id = document.getElementById('deviceId').value;

        fetch('/api/device/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, type, device_id })
        })
            .then(response => response.json())
            .then(data => {
                // Dynamically add the new device card to the dashboard
                const deviceCard = `
                    <div class="col-md-4 mb-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">${data.name}</h5>
                                <p class="card-text">
                                    Type: ${data.type}<br>
                                    Status: <span class="device-status" data-id="${data.id}">Off</span>
                                </p>
                                <div class="form-check form-switch">
                                    <input class="form-check-input device-toggle" type="checkbox" 
                                           data-id="${data.id}" id="device-${data.id}">
                                    <label class="form-check-label" for="device-${data.id}">Toggle</label>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                document.getElementById('devices-container').insertAdjacentHTML('beforeend', deviceCard);

                // Add event listener to the new toggle
                const newToggle = document.querySelector(`.device-toggle[data-id="${data.id}"]`);
                newToggle.addEventListener('change', function () {
                    const deviceId = this.dataset.id;
                    const newStatus = this.checked;

                    fetch(`/api/device/${deviceId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ status: newStatus })
                    })
                        .then(response => response.json())
                        .then(data => {
                            document.querySelector(`.device-status[data-id="${deviceId}"]`).textContent =
                                data.status ? 'On' : 'Off';
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            this.checked = !newStatus;
                        });
                });

                // Hide the modal and reset the form
                bootstrap.Modal.getInstance(document.getElementById('addDeviceModal')).hide();
                document.getElementById('addDeviceForm').reset();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});