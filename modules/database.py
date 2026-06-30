import sqlite3
import os


DB_PATH = os.environ.get("DB_PATH", "brain.sqlite")


def connect():
    conn = sqlite3.connect(DB_PATH)
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
        created_at TEXT,
        goal_type TEXT DEFAULT '短期'
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
        title TEXT DEFAULT '無称号',
        icon TEXT DEFAULT '✦',
        background TEXT DEFAULT 'default',
        bio TEXT DEFAULT '',
        coins INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    INSERT OR IGNORE INTO profile
    (id, title, icon, background, bio, coins)
    VALUES (1, '無称号', '✦', 'default', '', 0)
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

    conn.commit()
    conn.close()