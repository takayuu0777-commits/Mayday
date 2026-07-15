import uuid
from datetime import datetime

from modules.database import connect


GOAL_TYPES = [
    "短期",
    "中期",
    "長期"
]


def fetch_goals(user_id):
    if not user_id:
        return []

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM goals
    WHERE user_id = ?
      AND done = 0
    ORDER BY created_at DESC
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    return rows


def fetch_home_goals(user_id):
    result = {
        goal_type: None
        for goal_type in GOAL_TYPES
    }

    if not user_id:
        return result

    conn = connect()
    c = conn.cursor()

    for goal_type in GOAL_TYPES:
        c.execute("""
        SELECT *
        FROM goals
        WHERE user_id = ?
          AND done = 0
          AND goal_type = ?
        ORDER BY created_at DESC
        LIMIT 1
        """, (
            user_id,
            goal_type
        ))

        result[goal_type] = c.fetchone()

    conn.close()

    return result


def add_goal(
    user_id,
    title,
    goal_type
):
    clean_title = (
        title or ""
    ).strip()

    if not user_id or not clean_title:
        return False

    if goal_type not in GOAL_TYPES:
        goal_type = "短期"

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO goals
    (
        id,
        user_id,
        title,
        done,
        created_at,
        goal_type
    )
    VALUES (?, ?, ?, 0, ?, ?)
    """, (
        str(uuid.uuid4()),
        user_id,
        clean_title,
        datetime.now().isoformat(),
        goal_type
    ))

    conn.commit()
    conn.close()

    return True


def complete_goal(user_id, goal_id):
    if not user_id or not goal_id:
        return False

    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE goals
    SET done = 1
    WHERE id = ?
      AND user_id = ?
    """, (
        goal_id,
        user_id
    ))

    updated = c.rowcount == 1

    conn.commit()
    conn.close()

    return updated