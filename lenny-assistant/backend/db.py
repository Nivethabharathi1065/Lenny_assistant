"""
Simple SQLite persistence layer.

The assignment suggests Postgres (Supabase/Railway) — for a simple local
demo, SQLite gives the same "persistent storage of sessions/messages"
behavior with zero setup. Swapping to Postgres later just means changing
this file's connection string to use e.g. SQLAlchemy + psycopg2.
"""
import sqlite3
import uuid
import time
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "lenny.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            role TEXT,
            content TEXT,
            artifact TEXT,
            created_at REAL,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    """)
    conn.commit()
    conn.close()


def create_session(title="New Chat"):
    conn = get_conn()
    sid = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO sessions (id, title, created_at) VALUES (?, ?, ?)",
        (sid, title, time.time()),
    )
    conn.commit()
    conn.close()
    return sid


def list_sessions():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def session_exists(session_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    conn.close()
    return row is not None


def add_message(session_id, role, content, artifact=None):
    conn = get_conn()
    mid = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO messages (id, session_id, role, content, artifact, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (mid, session_id, role, content, artifact, time.time()),
    )
    conn.commit()
    conn.close()
    return mid


def get_messages(session_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
        (session_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
