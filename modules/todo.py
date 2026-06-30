import uuid
from datetime import datetime, date
from modules.database import connect


PRIORITIES = {
    "high": {"label": "高", "icon": "🔴"},
    "middle": {"label": "中", "icon": "🟡"},
    "low": {"label": "低", "icon": "🟢"}
}


def days_left(deadline):
    if not deadline:
        return ""

    try:
        target = datetime.strptime(deadline, "%Y-%m-%d").date()
        diff = (target - date.today()).days

        if diff > 0:
            return f"あと{diff}日"
        if diff == 0:
            return "今日まで"
        return "期限切れ"
    except Exception:
        return ""


def fetch_todos(limit=None):
    conn = connect()
    c = conn.cursor()

    sql = """
    SELECT *
    FROM todos
    WHERE done = 0
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

    if limit:
        sql += " LIMIT ?"
        rows = c.execute(sql, (limit,)).fetchall()
    else:
        rows = c.execute(sql).fetchall()

    conn.close()
    return rows


def add_todo(title, priority, deadline):
    title = (title or "").strip()

    if not title:
        return

    if priority not in PRIORITIES:
        priority = "middle"

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO todos
    (id, title, priority, deadline, done, created_at)
    VALUES (?, ?, ?, ?, 0, ?)
    """, (
        str(uuid.uuid4()),
        title,
        priority,
        deadline,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def complete_todo(todo_id):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE todos
    SET done = 1
    WHERE id = ?
    """, (todo_id,))

    conn.commit()
    conn.close()


def priority_icon(priority):
    return PRIORITIES.get(priority, PRIORITIES["middle"])["icon"]


def priority_label(priority):
    return PRIORITIES.get(priority, PRIORITIES["middle"])["label"]