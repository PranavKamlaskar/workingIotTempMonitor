An ESP8266 with a DHT11 sensor sends temperature and humidity data every minute to a Flask REST API running on your EC2 instance. That data is stored in an SQLite database and shown live on a simple web dashboard.


[ESP8266 + DHT11] 
   └── reads temp & humidity every 60s
        └── sends JSON via HTTP POST
             └── to Flask API on EC2: /api/data
                  └── stores in SQLite DB
                       └── /api/latest fetches most recent value
                            └── displayed in HTML dashboard every 5s

 Overview of the Project
We built a complete IoT system:

Hardware: ESP8266 + DHT11 sensor

Network: ESP8266 sends data over WiFi to a Flask REST API

Backend: Python Flask app running on an EC2 server, stores data in SQLite

Frontend: Dashboard shows live temperature and humidity readings in a browser

Built the Flask Server

What we did	Why	What happened
Created REST API (/api/data)	To receive POST requests from the ESP8266	Sensor readings were successfully received
Created SQLite database (sensor.db)	To store each temperature & humidity record	Data was saved with timestamp
Added /api/latest endpoint	To allow dashboard to fetch the most recent reading	Provided real-time access to latest sensor data
Used host='0.0.0.0' in app.run()	So Flask binds to all IP addresses, not just localhost	Made Flask accessible over the internet via public IP

IN T2 MICRO

sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git -y
sudo apt install python3-venv -y
python3 -m venv venv  
source venv/bin/activate   
pip install python-dotenv

mkdir iot-temp-monitor && cd iot-temp-monitor

vim requirements.txt       <!---refer file-->
pip3 install -r requirements.txt

vim app.py                 <!---refer file-->

mkdir templates/index.html      <!---refer file-->

python3 app.py        <!---test-->

Open your browser to:
http://<EC2_PUBLIC_IP>:5000

DHT11 VCC → 3.3V
DHT11 GND → GND
DHT11 DATA → D4 (GPIO2)

<!---refer misc--->
https://chatgpt.com/share/68126194-6ac8-8005-aac2-21dc21553d01

sudo apt install screen -y
screen -S flask
python3 app.py

 Step 1: Wired and Coded the ESP8266

What we did	Why	What happened
Connected DHT11 to ESP8266 (DATA → D4, VCC → 3.3V, GND → GND)	To physically read temperature & humidity	The sensor started returning readings to the microcontroller
Flashed code via Arduino IDE	To program the ESP8266 to read and send data	The ESP8266 began collecting data and sending it to the server every 60 seconds
Fixed the HTTPClient::begin() issue	New library versions require a WiFiClient parameter	Allowed the ESP8266 to make successful HTTP requests
🖥️ Step 2: Set Up an EC2 Instance

What we did	Why	What happened
Launched Ubuntu EC2 instance	Acts as a server in the cloud, accessible via IP	We had a cloud machine to run our Flask backend
Opened port 5000 in EC2 security group	Flask runs on port 5000 by default	Allowed the ESP8266 and browser to access the Flask server
Installed Python3, pip, Flask	To build the REST API	Enabled development and serving of HTTP endpoints
⚙️ Step 3: Built the Flask Server

What we did	Why	What happened
Created REST API (/api/data)	To receive POST requests from the ESP8266	Sensor readings were successfully received
Created SQLite database (sensor.db)	To store each temperature & humidity record	Data was saved with timestamp
Added /api/latest endpoint	To allow dashboard to fetch the most recent reading	Provided real-time access to latest sensor data
Used host='0.0.0.0' in app.run()	So Flask binds to all IP addresses, not just localhost	Made Flask accessible over the internet via public IP
🌐 Step 4: Built a Live Dashboard

What we did	Why	What happened
Created index.html in Flask’s templates folder	To serve a simple UI to view the data	Dashboard became available at http://your-ec2-ip:5000
Used JavaScript fetch() to call /api/latest	To get real-time updates every 5 seconds	Live sensor data started displaying automatically
🔁 Step 5: Confirmed System Flow


 Reads Temp & Humidity Every 60s
📍Arduino Code:
float temp = dht.readTemperature();
float hum = dht.readHumidity();
delay(60000); // Every 60 seconds

What we did	Why	What happened
Watched the ESP8266 logs in Serial Monitor	To verify successful HTTP POSTs	Response codes (like 201) confirmed success
Visited EC2 IP in browser	To confirm dashboard worked	Displayed latest values from the SQLite database
Verified database (sensor.db) existed	To check persistence	Values were saved each minute as new rows

Sends JSON via HTTP POST
📍Arduino Code:
WiFiClient client;
HTTPClient http;
http.begin(client, server);
http.addHeader("Content-Type", "application/json");

String payload = "{\"temperature\":" + String(temp) + ",\"humidity\":" + String(hum) + "}";
http.POST(payload);

Flask API Receives Data at /api/data
📍Flask Code (app.py):
@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    ...

Stores in SQLite DB
📍Flask Code (inside /api/data route):
with sqlite3.connect(DB_PATH) as conn:
    conn.execute(
        "INSERT INTO readings (temperature, humidity, timestamp) VALUES (?, ?, ?)",
        (data["temperature"], data["humidity"], datetime.now().isoformat())
    )
Location: Still in app.py, in the same route that handles /api/data.

📍Database Schema Setup:
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                humidity REAL,
                timestamp TEXT
            )
        ''')
✅ Called once at app startup to ensure DB/table exists.

    /api/latest Endpoint Fetches Most Recent Value
📍Flask Code (app.py):
@app.route("/api/latest", methods=["GET"])
def latest_data():
    row = conn.execute("SELECT temperature, humidity, timestamp FROM readings ORDER BY id DESC LIMIT 1").fetchone()
    ...

    Displayed on Dashboard Every 5 Seconds
📍HTML Dashboard Code (index.html):
<script>
  async function updateData() {
    const res = await fetch("/api/latest");
    const data = await res.json();
    document.getElementById("temp").innerText = data.temperature;
    ...
  }
  setInterval(updateData, 5000);  // Every 5 seconds
</script>


Let's add a real-time historical graph using:

✅ A new Flask endpoint: /api/history
✅ Chart.js to plot the latest temperature & humidity readings on the dashboard

Step 1: Add /api/history Endpoint to Flask (Backend)
📍In your app.py, add this route:                 <!--refer the file version 2-->

Step 2: Update HTML Template (Frontend)
📍In templates/index.html:
🔹 Add a <canvas> tag for the chart:
Insert this below your sensor values display:

Include Chart.js in the <head>:

Add JS code to fetch history and draw the chart:
Put this below your updateData() function in <script>:            <!--refer the index.html version2-->


###Telegram Alert Setup

 Step 1: Create a Telegram Bot
In Telegram, search for @BotFather

Start chat and type: /newbot

Choose a name and username (e.g., TempAlertBot)

You'll get a Bot Token like:

123456789:AAHh-sdf98asf7asF...etc
📌 Save this token

🔧 Step 2: Get Your chat_id
Send a message to your bot (e.g., "hi")

Open this URL in browser:
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
Look for "chat":{"id":...} — copy that chat_id

Email Alert Setup (Gmail)

🔧 Step 1: Get App Password (Gmail only)
Enable 2-step verification on your Google account

Visit: https://myaccount.google.com/apppasswords

Generate app password for “Mail”
Example: xkqj wpgs xxyz abcd                                        <!--refer youtube video-->

Update app.py for telegram and gmail                                <!--refer the versions/phase3-->



🔐 API Key Authentication (Header-Based)
🎯 Goal:
Only requests from devices that include a valid API key in the header will be accepted by your Flask server.

✅ Step 1: Define an API Key in Flask
In app.py, near the top (after your imports), add:

API_KEY = "your_super_secret_key"
Pick a strong random string — even abc123 is okay for testing, but in production use a longer key.

✅ Step 2: Update the /api/data route to check the key
Find your /api/data route and update it like this:

@app.route('/api/data', methods=['POST'])
def receive_data():
    # 🔐 Check for valid API key
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # ✅ Continue with normal data handling
    data = request.get_json()
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    timestamp = datetime.now()

    # ... store in DB, trigger alerts, etc ...
✅ Step 3: Update ESP8266 Code to Send API Key
In your Arduino sketch (.ino file), update the http.begin() and headers:

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// inside loop() or sendData() function:
HTTPClient http;
WiFiClient client;

http.begin(client, server); // Pass WiFiClient object
http.addHeader("Content-Type", "application/json");
http.addHeader("X-API-KEY", "your_super_secret_key");  // 🔐 Add this

int httpResponseCode = http.POST(jsonString);
Make sure "your_super_secret_key" matches the one in app.py.

✅ Step 4: Restart Flask Server
After editing app.py, restart your server:

python3 app.py
Test it from ESP — if the API key is correct, data flows. If wrong or missing, server responds:

{"error": "Unauthorized"}
🔐 You're Now Protected
This simple check ensures only authorized devices can POST data to your backend.




✅ Step-by-Step: Add /export CSV Download Route to Your Flask App
🔧 Step 1: Add a New Route to app.py
Open your app.py and below your other routes, add this:

python
Copy
Edit
import csv
from flask import Response
Then add the new route:

python
Copy
Edit
@app.route("/export", methods=["GET"])
def export_csv():
    def generate():
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT temperature, humidity, timestamp FROM readings ORDER BY id DESC")
            yield "temperature,humidity,timestamp\n"  # CSV header
            for row in cursor:
                yield f"{row[0]},{row[1]},{row[2]}\n"

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=sensor_data.csv"})
🧪 Step 2: Restart Flask Server
bash
Copy
Edit
python3 app.py
🌐 Step 3: Test in Browser
Go to:

arduino
Copy
Edit
http://<your-ec2-ip>:5000/export
It should download a file named sensor_data.csv with all your readings like:

makefile
Copy
Edit
temperature,humidity,timestamp
36.1,20.0,2025-04-30T16:59:10.123456
35.9,19.5,2025-04-30T16:58:10.987654
...

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

vim Dockerfile                                                          <!--refer the dockerfile--> 
vim requirements.txt
flask
requests
python-dotenv

vim .dockerignore
__pycache__/
*.pyc
.env
*.db

4. Build the Docker Image
In the same directory as your Dockerfile:

docker build -t iot-temp-app .
✅ 5. Run the Container
docker run -d -p 5000:5000 --env-file .env --name iot-container iot-temp-app
--env-file .env: Loads your secrets

-p 5000:5000: Maps container port to your EC2 public port

Now open your browser:

http://<your-ec2-public-ip>:5000
You should see the dashboard working — from inside Docker.



1. Update Your Project Structure
You’ll end up with something like:

iot-temp-monitor/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── .env
├── docker-compose.yml
├── nginx/
│   └── default.conf
└── templates/
    └── index.html
✅ 2. Create nginx/default.conf
# nginx/default.conf
server {
    listen 80;

    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
web:5000 refers to the Flask container's name (web) and port inside the Docker network.

✅ 3. Update/Create docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    container_name: flask_app
    env_file: .env
    ports:
      - "5000:5000"
    restart: always

  nginx:
    image: nginx:latest
    container_name: nginx_proxy
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - web
    restart: always
web builds from your Dockerfile and runs Flask.

nginx acts as a reverse proxy, listening on port 80.

✅ 4. Start Everything
From your project root:

docker compose up -d
Test in your browser:

http://<your-ec2-public-ip>
This should now route through Nginx → Flask.

✅ 5. Stop Everything
docker compose down






Step-by-Step: Frontend Enhancements for Summary & Filters
🔧 1. Update Your Flask /api/summary Route for Filtering
Replace your existing /api/summary route with this:

from datetime import datetime, timedelta

@app.route("/api/summary", methods=["GET"])
def summary():
    range_param = request.args.get("range", "all")
    
    query = """
        SELECT 
            AVG(temperature), MIN(temperature), MAX(temperature),
            AVG(humidity), MIN(humidity), MAX(humidity)
        FROM readings
    """
    params = ()

    if range_param == "24h":
        since = datetime.utcnow() - timedelta(days=1)
        query += " WHERE timestamp >= ?"
        params = (since.isoformat(),)
    elif range_param == "7d":
        since = datetime.utcnow() - timedelta(days=7)
        query += " WHERE timestamp >= ?"
        params = (since.isoformat(),)

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(query, params).fetchone()

    if row:
        avg_temp, min_temp, max_temp, avg_hum, min_hum, max_hum = row
        return jsonify({
            "temperature": {
                "avg": round(avg_temp, 2),
                "min": min_temp,
                "max": max_temp
            },
            "humidity": {
                "avg": round(avg_hum, 2),
                "min": min_hum,
                "max": max_hum
            }
        })
    else:
        return jsonify({"error": "No data available"}), 404
🖼️ 2. Update index.html
Replace your HTML <body> with this structure (or integrate into yours):


<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ESP8266 Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 40px;
    }
    h1 {
      color: #333;
    }
    .reading {
      font-size: 1.2em;
      margin-bottom: 10px;
    }
    .summary {
      margin-top: 30px;
    }
    #myChart {
      max-width: 800px;
      margin-top: 40px;
    }
    .range-buttons button {
      margin-right: 10px;
      padding: 6px 12px;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <h1>Temperature & Humidity</h1>

  <!-- Live Readings -->
  <div class="reading">Temperature: <span id="temp">--</span> °C</div>
  <div class="reading">Humidity: <span id="hum">--</span> %</div>
  <div class="reading">Time: <span id="timestamp">--</span></div>

  <!-- Summary Section -->
  <div class="summary">
    <h2>Summary (Filtered)</h2>
    <p><strong>Temperature:</strong> Avg: <span id="temp-avg">--</span>°C, Min: <span id="temp-min">--</span>°C, Max: <span id="temp-max">--</span>°C</p>
    <p><strong>Humidity:</strong> Avg: <span id="hum-avg">--</span>%, Min: <span id="hum-min">--</span>%, Max: <span id="hum-max">--</span>%</p>
  </div>

  <!-- Range Buttons -->
  <div class="range-buttons">
    <button onclick="loadData('all')">All</button>
    <button onclick="loadData('24h')">Last 24h</button>
    <button onclick="loadData('7d')">Last 7 days</button>
  </div>

  <!-- Chart -->
  <canvas id="myChart" width="800" height="400"></canvas>

  <script>
    let chart;

    async function updateLive() {
      const res = await fetch("/api/latest");
      const data = await res.json();
      document.getElementById("temp").innerText = data.temperature;
      document.getElementById("hum").innerText = data.humidity;
      document.getElementById("timestamp").innerText = data.timestamp;
    }

    async function loadSummary(range) {
      const res = await fetch(`/api/summary?range=${range}`);
      const data = await res.json();
      document.getElementById('temp-avg').textContent = data.temperature.avg;
      document.getElementById('temp-min').textContent = data.temperature.min;
      document.getElementById('temp-max').textContent = data.temperature.max;
      document.getElementById('hum-avg').textContent = data.humidity.avg;
      document.getElementById('hum-min').textContent = data.humidity.min;
      document.getElementById('hum-max').textContent = data.humidity.max;
    }

    async function loadHistory(range) {
      const res = await fetch(`/api/history?limit=50`); // Optional: support range later
      const data = await res.json();

      const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
      const tempData = data.map(d => d.temperature);
      const humData = data.map(d => d.humidity);

      if (chart) chart.destroy();

      chart = new Chart(document.getElementById("myChart"), {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Temperature (°C)",
              data: tempData,
              borderColor: "red",
              fill: false
            },
            {
              label: "Humidity (%)",
              data: humData,
              borderColor: "blue",
              fill: false
            }
          ]
        }
      });
    }

    async function loadData(range) {
      await loadSummary(range);
      await loadHistory(range);
    }

    updateLive();
    setInterval(updateLive, 5000);
    loadData("all");
  </script>
</body>
</html>




You're seeing UTC time because datetime.utcnow() returns time in Coordinated Universal Time, not your local time (India, which is UTC+5:30).

✅ Fix: Convert UTC to Indian Standard Time (IST)
Replace:

python
Copy
Edit
timestamp = datetime.utcnow().isoformat()
With:

python
Copy
Edit
from datetime import timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
timestamp = datetime.now(IST).isoformat()
This change should be made in:

python
Copy
Edit
@app.route("/api/data", methods=["POST"])
def receive_data():
    ...
    timestamp = datetime.now(IST).isoformat()
Optional: You can also format the timestamp for better readability (e.g., 02 May 2025, 6:48 PM) before sending it to the frontend, but since your frontend already uses new Date(timestamp).toLocaleTimeString() or similar, it should adapt automatically once the timestamp is in the correct time zone.


