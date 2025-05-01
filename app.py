from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
DB_PATH = "sensor.db"

# === CONFIGURATION ===

# Telegram
TELEGRAM_BOT_TOKEN = '7994386788:AAEfYyKCdkCOn6W21ksQK9hRqdFnXsMJu2s'
TELEGRAM_CHAT_ID = '727640208'

# Email (Gmail)
EMAIL_ADDRESS = "pranav.21.kamlaskar@gmail.com"
EMAIL_PASSWORD = "yofl wvuh asln xnpx"
EMAIL_RECEIVER = "pranav.21.kamlaskar@gmail.com"

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
    data = request.get_json()
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    timestamp = datetime.utcnow().isoformat()

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

# === MAIN ===

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

