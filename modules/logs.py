import uuid
from datetime import datetime

from modules.database import connect


def classify(text):
    if "仕事" in text:
        return "仕事"

    if any(word in text for word in ["勉強", "学習", "読書"]):
        return "学習"

    if any(word in text for word in ["映画", "漫画", "アニメ", "ゲーム"]):
        return "メディア"

    if any(word in text for word in ["買い物", "購入"]):
        return "買い物"

    if "目標" in text:
        return "目標"

    return "思考"


def summarize(text):
    return (text or "")[:40]


def add_coin(user_id, amount):
    if not user_id:
        return False

    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE user_profiles
    SET coins = coins + ?
    WHERE user_id = ?
    """, (
        amount,
        user_id
    ))

    conn.commit()
    conn.close()

    return True


def save(user_id, text):
    clean_text = (text or "").strip()

    if not user_id or not clean_text:
        return False

    now = datetime.now()

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO logs
    (
        id,
        user_id,
        text,
        category,
        summary,
        created_at,
        date_key
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        user_id,
        clean_text,
        classify(clean_text),
        summarize(clean_text),
        now.isoformat(),
        now.strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    add_coin(user_id, 1)

    return True


def fetch_all(user_id):
    if not user_id:
        return []

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM logs
    WHERE user_id = ?
    ORDER BY created_at DESC
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    return rows