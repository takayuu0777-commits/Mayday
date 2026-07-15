import uuid
from datetime import datetime

from modules.database import connect


ICON_RULES = {
    "牛乳": "🥛",
    "水": "💧",
    "米": "🍚",
    "パン": "🍞",
    "卵": "🥚",
    "肉": "🥩",
    "魚": "🐟",
    "野菜": "🥬",
    "薬": "💊",
    "服": "👕",
    "靴": "👟",
    "本": "📚",
    "電池": "🔋",
    "充電": "🔌",
    "ティッシュ": "🧻",
    "洗剤": "🧴"
}


def guess_icon(name):
    clean_name = name or ""

    for key, icon in ICON_RULES.items():
        if key in clean_name:
            return icon

    return "🛒"


def fetch_items(user_id):
    if not user_id:
        return []

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM shopping
    WHERE user_id = ?
      AND done = 0
    ORDER BY created_at DESC
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    return rows


def add_item(user_id, name):
    clean_name = (
        name or ""
    ).strip()

    if not user_id or not clean_name:
        return False

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO shopping
    (
        id,
        user_id,
        name,
        done,
        created_at
    )
    VALUES (?, ?, ?, 0, ?)
    """, (
        str(uuid.uuid4()),
        user_id,
        clean_name,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return True


def complete_item(user_id, item_id):
    if not user_id or not item_id:
        return False

    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE shopping
    SET done = 1
    WHERE id = ?
      AND user_id = ?
    """, (
        item_id,
        user_id
    ))

    updated = c.rowcount == 1

    conn.commit()
    conn.close()

    return updated