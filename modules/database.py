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
        converted_query = query.replace("?", "%s")
        self.cursor.execute(converted_query, params or ())
        return self

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def rowcount(self):
        return self.cursor.rowcount


class PostgresConnection:
    def __init__(self, connection):
        self.connection = connection

    def cursor(self):
        from psycopg2.extras import RealDictCursor

        cursor = self.connection.cursor(
            cursor_factory=RealDictCursor
        )

        return PostgresCursor(cursor)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def connect():
    if is_postgres():
        import psycopg2

        connection = psycopg2.connect(
            DATABASE_URL,
            connect_timeout=10
        )

        return PostgresConnection(connection)

    database_directory = os.path.dirname(DB_PATH)

    if database_directory:
        os.makedirs(
            database_directory,
            exist_ok=True
        )

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def add_column_if_missing(
    cursor,
    table_name,
    column_name,
    definition
):
    if is_postgres():
        cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = ?
        """, (table_name,))

        existing_columns = [
            row["column_name"]
            for row in cursor.fetchall()
        ]

    else:
        cursor.execute(
            f"PRAGMA table_info({table_name})"
        )

        existing_columns = [
            row["name"]
            for row in cursor.fetchall()
        ]

    if column_name not in existing_columns:
        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {definition}
            """
        )


def create_users_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)


def create_main_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id TEXT PRIMARY KEY,
        text TEXT,
        category TEXT,
        summary TEXT,
        created_at TEXT,
        date_key TEXT,
        user_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS library (
        id TEXT PRIMARY KEY,
        title TEXT,
        genre TEXT,
        rating INTEGER DEFAULT 0,
        created_at TEXT,
        user_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id TEXT PRIMARY KEY,
        library_id TEXT,
        text TEXT,
        created_at TEXT,
        user_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        title TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT,
        goal_type TEXT DEFAULT '短期',
        user_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shopping (
        id TEXT PRIMARY KEY,
        name TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT,
        user_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id TEXT PRIMARY KEY,
        title TEXT,
        priority TEXT DEFAULT 'middle',
        deadline TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT,
        user_id TEXT
    )
    """)

    if is_postgres():
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_memos (
            id SERIAL PRIMARY KEY,
            date_key TEXT,
            text TEXT,
            icon TEXT DEFAULT '📝',
            created_at TEXT,
            user_id TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prefectures (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE,
            status TEXT DEFAULT 'none',
            user_id TEXT
        )
        """)

    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_memos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_key TEXT,
            text TEXT,
            icon TEXT DEFAULT '📝',
            created_at TEXT,
            user_id TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prefectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            status TEXT DEFAULT 'none',
            user_id TEXT
        )
        """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY,
        title TEXT DEFAULT '無称号',
        icon TEXT DEFAULT '✦',
        background TEXT DEFAULT 'default',
        bio TEXT DEFAULT '',
        coins INTEGER DEFAULT 0,
        user_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_days (
        date_key TEXT PRIMARY KEY,
        created_at TEXT,
        user_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements_unlocked (
        id TEXT PRIMARY KEY,
        unlocked_at TEXT,
        user_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        setting_key TEXT,
        setting_value TEXT
    )
    """)


def add_missing_columns(cursor):
    add_column_if_missing(
        cursor,
        "library",
        "rating",
        "INTEGER DEFAULT 0"
    )

    add_column_if_missing(
        cursor,
        "goals",
        "goal_type",
        "TEXT DEFAULT '短期'"
    )

    add_column_if_missing(
        cursor,
        "profile",
        "background",
        "TEXT DEFAULT 'default'"
    )

    add_column_if_missing(
        cursor,
        "profile",
        "bio",
        "TEXT DEFAULT ''"
    )

    add_column_if_missing(
        cursor,
        "profile",
        "coins",
        "INTEGER DEFAULT 0"
    )

    user_tables = [
        "logs",
        "library",
        "reviews",
        "goals",
        "shopping",
        "todos",
        "calendar_memos",
        "prefectures",
        "profile",
        "login_days",
        "achievements_unlocked"
    ]

    for table_name in user_tables:
        add_column_if_missing(
            cursor,
            table_name,
            "user_id",
            "TEXT"
        )


def ensure_old_profile(cursor):
    if is_postgres():
        cursor.execute("""
        INSERT INTO profile
        (
            id,
            title,
            icon,
            background,
            bio,
            coins
        )
        VALUES (
            1,
            '無称号',
            '✦',
            'default',
            '',
            0
        )
        ON CONFLICT (id) DO NOTHING
        """)

    else:
        cursor.execute("""
        INSERT OR IGNORE INTO profile
        (
            id,
            title,
            icon,
            background,
            bio,
            coins
        )
        VALUES (
            1,
            '無称号',
            '✦',
            'default',
            '',
            0
        )
        """)


def init():
    connection = connect()

    try:
        cursor = connection.cursor()

        create_users_table(cursor)
        create_main_tables(cursor)
        add_missing_columns(cursor)
        ensure_old_profile(cursor)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()