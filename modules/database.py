import sqlite3
import os
from datetime import datetime

DB = os.path.join(os.getcwd(), "brain.sqlite")


def connect():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def now_text():
    return datetime.now().isoformat()


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
        rating INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id TEXT PRIMARY KEY,
        library_id TEXT,
        text TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        title TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS shopping (
        id TEXT PRIMARY KEY,
        name TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY,
        username TEXT,
        title TEXT,
        icon TEXT,
        coins INTEGER DEFAULT 100,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS login_days (
        date_key TEXT PRIMARY KEY,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS achievements_unlocked (
        id TEXT PRIMARY KEY,
        unlocked_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS life_events (
        id TEXT PRIMARY KEY,
        title TEXT,
        emoji TEXT,
        event_date TEXT,
        description TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    INSERT OR IGNORE INTO profile
    (id, username, title, icon, coins, created_at)
    VALUES
    (1, 'ユーザー', '無称号', '🧠', 100, ?)
    """, (now_text(),))

    conn.commit()
    conn.close()