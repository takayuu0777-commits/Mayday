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
    for key, icon in ICON_RULES.items():
        if key in name:
            return icon
    return "🛒"


def fetch_items():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM shopping
    WHERE done = 0
    ORDER BY created_at DESC
    """)

    rows = c.fetchall()
    conn.close()
    return rows


def add_item(name):
    name = (name or "").strip()

    if not name:
        return

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO shopping
    (id, name, done, created_at)
    VALUES (?, ?, 0, ?)
    """, (
        str(uuid.uuid4()),
        name,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def complete_item(item_id):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE shopping
    SET done = 1
    WHERE id = ?
    """, (item_id,))

    conn.commit()
    conn.close()