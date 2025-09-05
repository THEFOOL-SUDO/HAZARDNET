# app/db.py
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), "hazardnet.db")

def init_db():
    con = sqlite3.connect(DB, check_same_thread=False)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id TEXT PRIMARY KEY,
        source TEXT,
        text TEXT,
        lat REAL,
        lon REAL,
        media_url TEXT,
        embedding BLOB,
        cluster_id INTEGER,
        created_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cluster_id INTEGER UNIQUE,
        title TEXT,
        centroid_lat REAL,
        centroid_lon REAL,
        confidence REAL,
        last_seen TEXT
    )""")
    con.commit()
    return con

DB_CONN = init_db()
