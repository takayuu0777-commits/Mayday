import uuid
from datetime import date, datetime

from modules.database import connect


PRIORITIES = {
    "high": {
        "label": "高",
        "icon": "🔴"
    },
    "middle": {
        "label": "中",
        "icon": "🟡"
    },
    "low": {
        "label": "低",
        "icon": "🟢"
    }
}


def days_left(deadline):
    if not deadline:
        return ""

    try:
        target = datetime.strptime(
            deadline,
            "%Y-%m-%d"
        ).date()

        difference = (
            target - date.today()
        ).days

        if difference > 0:
            return f"あと{difference}日"

        if difference == 0:
            return "今日まで"

        return "期限切れ"

    except (TypeError, ValueError):
        return ""


def fetch_todos(user_id, limit=None):
    if not user_id:
        return []

    conn = connect()
    c = conn.cursor()

    sql = """
    SELECT *
    FROM todos
    WHERE user_id = ?
      AND done = 0
    ORDER BY
        CASE priority
            WHEN 'high' THEN 1
            WHEN 'middle' THEN 2
            WHEN 'low' THEN 3
            ELSE 4
        END,
        deadline ASC,
        created_at DESC
    """

    params = [user_id]

    if limit:
        sql += " LIMIT ?"
        params.append(limit)

    c.execute(
        sql,
        tuple(params)
    )

    rows = c.fetchall()
    conn.close()

    return rows


def add_todo(
    user_id,
    title,
    priority,
    deadline
):
    clean_title = (
        title or ""
    ).strip()

    clean_deadline = (
        deadline or ""
    ).strip()

    if not user_id or not clean_title:
        return False

    if priority not in PRIORITIES:
        priority = "middle"

    if clean_deadline:
        try:
            datetime.strptime(
                clean_deadline,
                "%Y-%m-%d"
            )
        except ValueError:
            clean_deadline = ""

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO todos
    (
        id,
        user_id,
        title,
        priority,
        deadline,
        done,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, 0, ?)
    """, (
        str(uuid.uuid4()),
        user_id,
        clean_title,
        priority,
        clean_deadline,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return True


def complete_todo(user_id, todo_id):
    if not user_id or not todo_id:
        return False

    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE todos
    SET done = 1
    WHERE id = ?
      AND user_id = ?
    """, (
        todo_id,
        user_id
    ))

    updated = c.rowcount == 1

    conn.commit()
    conn.close()

    return updated


def priority_icon(priority):
    return PRIORITIES.get(
        priority,
        PRIORITIES["middle"]
    )["icon"]


def priority_label(priority):
    return PRIORITIES.get(
        priority,
        PRIORITIES["middle"]
    )["label"]