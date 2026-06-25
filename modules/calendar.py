import uuid
from datetime import datetime
from modules.database import connect


def fetch_data():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT date_key, category
    FROM logs
    """)

    rows = c.fetchall()

    conn.close()

    data = {}

    for row in rows:
        date = row["date_key"]
        category = row["category"]

        data.setdefault(date, {})
        data[date][category] = data[date].get(category, 0) + 1

    return data


def fetch_life_events():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM life_events
    ORDER BY event_date DESC
    """)

    rows = c.fetchall()

    conn.close()
    return rows


def add_life_event(title, emoji, event_date, description):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO life_events
    (id, title, emoji, event_date, description, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        title,
        emoji,
        event_date,
        description,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()