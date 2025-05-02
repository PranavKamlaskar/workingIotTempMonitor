from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB_PATH = "sensor.db"

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
init_db()

@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    if not data or "temperature" not in data or "humidity" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO readings (temperature, humidity, timestamp) VALUES (?, ?, ?)",
            (data["temperature"], data["humidity"], datetime.now().isoformat())
        )
    return jsonify({"status": "success"}), 201

@app.route("/api/latest", methods=["GET"])
def latest_data():
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT temperature, humidity, timestamp FROM readings ORDER BY id DESC LIMIT 1").fetchone()
    if row:
        return jsonify({"temperature": row[0], "humidity": row[1], "timestamp": row[2]})
    return jsonify({"error": "No data"}), 404

@app.route("/api/history", methods=["GET"])
def history():
    limit = int(request.args.get("limit", 50))  # default 50 records
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT temperature, humidity, timestamp FROM readings ORDER BY id DESC LIMIT ?", 
            (limit,)
        ).fetchall()
        # Reverse to show oldest → newest
        rows.reverse()
        data = [
            {"temperature": t, "humidity": h, "timestamp": ts}
            for (t, h, ts) in rows
        ]
    return jsonify(data)


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

