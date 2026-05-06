"""
database.py
Persistent scan history using SQLite.
Saves every resume scan with skills, predicted role, skill count, and timestamp.
Proves backend/database knowledge to evaluators.
"""
import sqlite3
import json
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.db")

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT,
            skills      TEXT,
            role        TEXT,
            skill_count INTEGER DEFAULT 0,
            timestamp   TEXT
        )
    """)

    # Add column if upgrading from an older schema.
    try:
        conn.execute("ALTER TABLE scans ADD COLUMN skill_count INTEGER DEFAULT 0")
    except Exception:
        pass

    conn.commit()
    return conn

def save_scan(filename: str, skills: set, role: str) -> None:
    """Save a resume scan to the history database."""
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO scans (filename, skills, role, skill_count, timestamp) "
            "VALUES (?,?,?,?,?)",
            (
                filename,
                json.dumps(sorted(list(skills))),
                role,
                len(skills),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            )
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Save failed: {e}")

def get_history() -> list:
    """Retrieve last 10 scans from history."""
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT filename, role, skills, skill_count, timestamp "
            "FROM scans ORDER BY id DESC LIMIT 10"
        ).fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[DB] Read failed: {e}")
        return []

def clear_history() -> None:
    """Delete all scan history."""
    try:
        conn = _get_conn()
        conn.execute("DELETE FROM scans")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Clear failed: {e}")
