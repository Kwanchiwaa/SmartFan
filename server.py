from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# ข้อมูลเซ็นเซอร์
sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "pm25": 0
}

@app.route("/dashboard")
def dashboard():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Smart Factory Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://bernii.github.io/gauge.js/dist/gauge.min.js"></script>
        <style>
            body { font-family: sans-serif; text-align: center; margin: 20px; }
            .gauge-container { width: 200px; display: inline-block; margin: 20px; }
            #pmChart { width: 100%; max-width: 600px; margin: auto; }
            .val-text { font-size: 20px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>Smart Factory Dashboard</h1>

        <canvas id="pmChart" height="120"></canvas>

        <div class="gauge-container">
            <h3>Temperature</h3>
            <canvas id="tempGauge" width="200" height="200"></canvas>
            <div id="tempVal" class="val-text">-- °C</div>
        </div>

        <div class="gauge-container">
            <h3>Humidity</h3>
            <canvas id="humGauge" width="200" height="200"></canvas>
            <div id="humVal" class="val-text">-- %</div>
        </div>

        <script>
            const pmCtx = document.getElementById('pmChart').getContext('2d');
            const pmChart = new Chart(pmCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'PM2.5',
                        data: [],
                        borderColor: 'blue',
                        tension: 0.2,
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        y: { min: 0, max: 160 }
                    }
                }
            });

            const tempGauge = new Gauge(document.getElementById("tempGauge")).setOptions({
                angle: 0, lineWidth: 0.3, radiusScale: 1,
                pointer: { length: 0.6, strokeWidth: 0.04 },
                staticZones: [
                    {strokeStyle: "#30B32D", min: 0, max: 30},
                    {strokeStyle: "#FFDD00", min: 30, max: 40},
                    {strokeStyle: "#F03E3E", min: 40, max: 50}
                ],
                maxValue: 50, animationSpeed: 32
            });
            tempGauge.maxValue = 50;

            const humGauge = new Gauge(document.getElementById("humGauge")).setOptions({
                angle: 0, lineWidth: 0.3, radiusScale: 1,
                pointer: { length: 0.6, strokeWidth: 0.04 },
                staticZones: [
                    {strokeStyle: "#3E8EF7", min: 0, max: 40},
                    {strokeStyle: "#FFDD00", min: 40, max: 70},
                    {strokeStyle: "#F03E3E", min: 70, max: 100}
                ],
                maxValue: 100, animationSpeed: 32
            });
            humGauge.maxValue = 100;

            let pmHistory = [];
            let timeLabels = [];

            // เชื่อมต่อ WebSocket
            const socket = io.connect('http://' + document.domain + ':' + location.port);
            socket.on('sensor_data', function(data) {
                const temp = data.temperature || 0;
                const hum = data.humidity || 0;
                const pm = data.pm25 || 0;

                // อัปเดตแสดงข้อมูล
                tempGauge.set(temp);
                humGauge.set(hum);
                document.getElementById("tempVal").innerText = `${temp} °C`;
                document.getElementById("humVal").innerText = `${hum} %`;

                const now = new Date();
                const timeLabel = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
                timeLabels.push(timeLabel);
                pmHistory.push(pm);

                if (pmHistory.length > 10) {
                    pmHistory.shift();
                    timeLabels.shift();
                }

                pmChart.data.labels = timeLabels;
                pmChart.data.datasets[0].data = pmHistory;
                pmChart.update();
            });

        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

# ฟังก์ชันสำหรับส่งข้อมูลเซ็นเซอร์
@socketio.on('connect')
def handle_connect():
    emit('sensor_data', sensor_data, broadcast=True)

# API สำหรับรับข้อมูลจากเซ็นเซอร์
@app.route("/update_sensor", methods=["POST"])
def update_sensor():
    data = request.get_json()
    if data:
        sensor_data.update(data)
        socketio.emit('sensor_data', sensor_data, broadcast=True)
        return jsonify({"status": "success"})
    return jsonify({"error": "Invalid data"}), 400

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
