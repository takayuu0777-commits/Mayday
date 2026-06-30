from datetime import datetime
from collections import defaultdict
from modules.database import connect


def fetch_data():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM logs
    ORDER BY created_at DESC
    """)

    rows = c.fetchall()
    conn.close()

    data = defaultdict(list)

    for row in rows:
        date_key = row["date_key"] or row["created_at"][:10]
        data[date_key].append(row)

    return dict(data)


def calendar_icons():
    data = fetch_data()
    result = {}

    for date_key, logs in data.items():
        icons = []

        for log in logs:
            category = log["category"] or "その他"

            if category == "学習":
                icons.append("📚")
            elif category == "仕事":
                icons.append("💼")
            elif category == "メディア":
                icons.append("🎬")
            elif category == "健康":
                icons.append("💪")
            elif category == "買い物":
                icons.append("🛒")
            else:
                icons.append("✦")

        result[date_key] = icons[:4]

    return result


def fetch_life_events():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS life_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        event_date TEXT,
        description TEXT
    )
    """)

    c.execute("""
    SELECT *
    FROM life_events
    ORDER BY event_date DESC
    """)

    rows = c.fetchall()
    conn.close()
    return rows


def add_life_event(title, event_date, description):
    title = (title or "").strip()
    event_date = (event_date or "").strip()
    description = (description or "").strip()

    if not title or not event_date:
        return

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO life_events
    (title, event_date, description)
    VALUES (?, ?, ?)
    """, (
        title,
        event_date,
        description
    ))

    conn.commit()
    conn.close()