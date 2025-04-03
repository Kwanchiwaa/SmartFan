from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Store sensor values in memory
sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "soil_moisture": 0,
    "threshold": 50  # Default threshold
}

# Endpoint for ESP32 / M5Stack to get sensor values and threshold
@app.route('/', methods=['GET'])
def get_data():
    return jsonify(sensor_data)

# Endpoint for ESP32 to POST updated sensor values
@app.route('/', methods=['POST'])
def update_data():
    data = request.get_json()
    if data:
        sensor_data.update(data)
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "Invalid data"}), 400

# GUI to view and update threshold
@app.route('/set_threshold', methods=['GET', 'POST'])
def set_threshold():
    message = ""
    if request.method == 'POST':
        try:
            new_threshold = int(request.form['threshold'])
            sensor_data['threshold'] = new_threshold
            message = f"✅ Threshold updated to {new_threshold}"
        except:
            message = "❌ Invalid input. Please enter a number."

    # Enhanced HTML page
    html = '''
    <html>
        <head>
            <title>IoT Control Panel</title>
        </head>
        <body style="font-family:sans-serif; max-width: 600px; margin: auto; padding: 20px;">
            <h2>🌿 IoT Sensor Dashboard</h2>
            <table border="1" cellpadding="10" cellspacing="0">
                <tr><th>Sensor</th><th>Value</th></tr>
                <tr><td>🌡️ Temperature</td><td>{{ temperature }} °C</td></tr>
                <tr><td>💧 Humidity</td><td>{{ humidity }} %</td></tr>
                <tr><td>🌱 Soil Moisture</td><td>{{ soil_moisture }} %</td></tr>
                <tr><td>🎚️ Threshold</td><td><b>{{ threshold }} %</b></td></tr>
            </table>

            <h3>🔧 Update Threshold</h3>
            <form method="POST">
                <label for="threshold">New Threshold (%):</label><br>
                <input type="number" name="threshold" min="0" max="100" value="{{ threshold }}" required>
                <br><br>
                <button type="submit">Update</button>
            </form>

            <p style="color: green;">{{ message }}</p>
        </body>
    </html>
    '''
    return render_template_string(
        html,
        temperature=sensor_data["temperature"],
        humidity=sensor_data["humidity"],
        soil_moisture=sensor_data["soil_moisture"],
        threshold=sensor_data["threshold"],
        message=message
    )
