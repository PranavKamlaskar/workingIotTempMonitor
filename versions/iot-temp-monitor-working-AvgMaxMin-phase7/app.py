from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText
import os 
from dotenv import load_dotenv
import csv
from flask import Response
from datetime import datetime, timedelta, timezone



load_dotenv()

# Use secrets from .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
DB_PATH = "sensor.db"


# === HELPER FUNCTIONS ===

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

def send_email_alert(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# === ROUTES ===

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data", methods=["POST"])
def receive_data():
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    IST= timezone(timedelta(hours=5, minutes=30))
    timestamp = datetime.now(IST).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO readings (temperature, humidity, timestamp) VALUES (?, ?, ?)", 
                     (temperature, humidity, timestamp))
        conn.commit()

    # === ALERT CONDITIONS ===
    if temperature > 30 or humidity < 25:
        alert_msg = f"⚠️ Alert!\nTemp: {temperature}°C\nHumidity: {humidity}%"

        # Send Telegram alert
        send_telegram_alert(alert_msg)

        # Send Email alert
        subject = "Sensor Alert!"
        body = f"Temperature: {temperature}°C\nHumidity: {humidity}%"
        send_email_alert(subject, body)

    return jsonify({"status": "success"}), 200


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



@app.route("/api/latest", methods=["GET"])
def latest():
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT temperature, humidity, timestamp FROM readings ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row:
            temp, hum, ts = row
            return jsonify({
                "temperature": temp,
                "humidity": hum,
                "timestamp": ts
            })
        else:
            return jsonify({"error": "No data"}), 404

@app.route("/api/history", methods=["GET"])
def history():
    limit = int(request.args.get("limit", 50))
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT temperature, humidity, timestamp FROM readings ORDER BY id DESC LIMIT ?", 
            (limit,)
        ).fetchall()
        rows.reverse()
        data = [
            {"temperature": t, "humidity": h, "timestamp": ts}
            for (t, h, ts) in rows
        ]
    return jsonify(data)


@app.route("/api/summary", methods=["GET"])
def summary():
    range_param = request.args.get("range", "all")
    query = """
        SELECT
            AVG(temperature), MIN(temperature), MAX(temperature),
            AVG(humidity), MIN(humidity), MAX(humidity)
        FROM readings
    """
    params=()

    if range_param == "24h":
        since= datetime.utcnow() - timedelta(days=1)
        query += "WHERE timestamp >= ?"
        params = (since.isoformat(),)
    elif range_param == "7d":
        since = datetime.utcnow() - timedelta(days=7)
        query += " WHERE timestamp >= ?"
        params = (since.isoformat(),)
        
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(query, params).fetchone()

    if row:
        avg_temp, min_temp, max_temp, avg_hum, min_hum, max_hum =row
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

# === MAIN ===

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

