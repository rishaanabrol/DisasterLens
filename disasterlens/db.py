import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "disaster.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL,
            lon REAL,
            hazard_type TEXT,
            hazard_confidence REAL,
            hazard_distribution TEXT,
            priority TEXT,
            recommended_action TEXT,
            alert TEXT,
            image_base64 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_report(lat, lon, prediction, image_base64):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (
            lat, lon, hazard_type, hazard_confidence, hazard_distribution,
            priority, recommended_action, alert, image_base64
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        lat, lon,
        prediction["hazard_type"],
        prediction["hazard_confidence"],
        json.dumps(prediction["hazard_distribution"]),
        prediction["priority"],
        prediction["recommended_action"],
        prediction["alert"],
        image_base64
    ))
    report_id = c.lastrowid
    conn.commit()
    conn.close()
    return report_id

def list_reports():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM reports ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    
    reports = []
    for row in rows:
        r = dict(row)
        r["hazard_distribution"] = json.loads(r["hazard_distribution"])
        reports.append(r)
    return reports
