import sqlite3
import os

DB = os.path.join(os.getcwd(), "brain.sqlite")


def connect():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id TEXT PRIMARY KEY,
        text TEXT,
        category TEXT,
        summary TEXT,
        created_at TEXT,
        date_key TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS library (
        id TEXT PRIMARY KEY,
        title TEXT,
        genre TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()