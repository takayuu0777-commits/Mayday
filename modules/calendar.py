import uuid
from datetime import datetime
from modules.database import connect


def classify(text):
    if "仕事" in text:
        return "仕事"
    if "勉強" in text or "学習" in text or "読書" in text:
        return "学習"
    if "映画" in text or "漫画" in text or "アニメ" in text or "ゲーム" in text:
        return "メディア"
    if "買い物" in text or "購入" in text:
        return "買い物"
    if "目標" in text:
        return "目標"
    return "思考"


def summarize(text):
    return text[:40]


def save(text):
    conn = connect()
    c = conn.cursor()

    now = datetime.now()

    c.execute("""
    INSERT INTO logs
    (id, text, category, summary, created_at, date_key)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        text,
        classify(text),
        summarize(text),
        now.isoformat(),
        now.strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()


def fetch_all():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM logs ORDER BY created_at DESC")
    rows = c.fetchall()

    conn.close()
    return rows