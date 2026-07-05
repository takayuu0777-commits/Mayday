import os
import sqlite3


DATABASE_URL = os.environ.get("DATABASE_URL")
DB_PATH = os.environ.get("DB_PATH", "brain.sqlite")


def is_postgres():
    return bool(DATABASE_URL)


class PostgresCursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, params=None):
        query = query.replace("?", "%s")
        self.cursor.execute(query, params or ())
        return self

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()


class PostgresConnection:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        from psycopg2.extras import RealDictCursor
        return PostgresCursor(self.conn.cursor(cursor_factory=RealDictCursor))

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def connect():
    if is_postgres():
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return PostgresConnection(conn)

    db_dir = os.path.dirname(DB_PATH)

    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def add_column_if_missing(cursor, table, column, definition):
    if is_postgres():
        cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        """, (table,))

        columns = [row["column_name"] for row in cursor.fetchall()]

        if column not in columns:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            )

    else:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row["name"] for row in cursor.fetchall()]

        if column not in columns:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            )


def init():
    conn = connect()
    c = conn.cursor()

    if is_postgres():
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
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            title TEXT,
            priority TEXT DEFAULT 'middle',
            deadline TEXT,
            done INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS calendar_memos (
            id SERIAL PRIMARY KEY,
            date_key TEXT,
            text TEXT,
            icon TEXT DEFAULT '📝',
            created_at TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS prefectures (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE,
            status TEXT DEFAULT 'none'
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
        INSERT INTO profile
        (id, title, icon, background, bio, coins)
        VALUES (1, '無称号', '✦', 'default', '', 0)
        ON CONFLICT (id) DO NOTHING
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

    else:
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
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            title TEXT,
            priority TEXT DEFAULT 'middle',
            deadline TEXT,
            done INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS calendar_memos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_key TEXT,
            text TEXT,
            icon TEXT DEFAULT '📝',
            created_at TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS prefectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            status TEXT DEFAULT 'none'
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

    add_column_if_missing(c, "library", "rating", "INTEGER DEFAULT 0")
    add_column_if_missing(c, "goals", "goal_type", "TEXT DEFAULT '短期'")
    add_column_if_missing(c, "profile", "background", "TEXT DEFAULT 'default'")
    add_column_if_missing(c, "profile", "bio", "TEXT DEFAULT ''")
    add_column_if_missing(c, "profile", "coins", "INTEGER DEFAULT 0")

    conn.commit()
    conn.close()