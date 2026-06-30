import uuid
from datetime import datetime
from modules.database import connect


GOAL_TYPES = [
    "短期",
    "中期",
    "長期"
]


def fetch_goals():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM goals
    WHERE done = 0
    ORDER BY created_at DESC
    """)

    rows = c.fetchall()
    conn.close()
    return rows


def fetch_home_goals():
    conn = connect()
    c = conn.cursor()

    result = {}

    for goal_type in GOAL_TYPES:
        c.execute("""
        SELECT *
        FROM goals
        WHERE done = 0
        AND goal_type = ?
        ORDER BY created_at DESC
        LIMIT 1
        """, (goal_type,))

        result[goal_type] = c.fetchone()

    conn.close()
    return result


def add_goal(title, goal_type):
    title = (title or "").strip()

    if not title:
        return

    if goal_type not in GOAL_TYPES:
        goal_type = "短期"

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO goals
    (id, title, done, created_at, goal_type)
    VALUES (?, ?, 0, ?, ?)
    """, (
        str(uuid.uuid4()),
        title,
        datetime.now().isoformat(),
        goal_type
    ))

    conn.commit()
    conn.close()


def complete_goal(goal_id):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE goals
    SET done = 1
    WHERE id = ?
    """, (goal_id,))

    conn.commit()
    conn.close()