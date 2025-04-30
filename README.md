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

