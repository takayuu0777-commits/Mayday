import uuid
from datetime import datetime
from modules.database import connect


GENRES = [
    "アニメ",
    "漫画",
    "映画",
    "ゲーム",
    "小説",
    "音楽",
    "ドラマ",
    "YouTube",
    "その他"
]


def guess_genre(title):
    text = title

    if "映画" in text:
        return "映画"

    if "漫画" in text or "マンガ" in text:
        return "漫画"

    if "ゲーム" in text:
        return "ゲーム"

    if "小説" in text or "本" in text:
        return "小説"

    if "音楽" in text or "曲" in text:
        return "音楽"

    if "ドラマ" in text:
        return "ドラマ"

    if "YouTube" in text or "youtube" in text:
        return "YouTube"

    if "アニメ" in text:
        return "アニメ"

    return "その他"


def add_coin(amount):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE profile
    SET coins = coins + ?
    WHERE id = 1
    """, (amount,))

    conn.commit()
    conn.close()


def add_item(title, genre=None, rating=0):
    if not genre:
        genre = guess_genre(title)

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO library
    (id, title, genre, rating, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        title,
        genre,
        rating,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    add_coin(2)


def delete_item(item_id):
    conn = connect()
    c = conn.cursor()

    c.execute("DELETE FROM reviews WHERE library_id = ?", (item_id,))
    c.execute("DELETE FROM library WHERE id = ?", (item_id,))

    conn.commit()
    conn.close()


def update_item(item_id, title, genre, rating):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE library
    SET title = ?,
        genre = ?,
        rating = ?
    WHERE id = ?
    """, (title, genre, rating, item_id))

    conn.commit()
    conn.close()


def add_review(item_id, text):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO reviews
    (id, library_id, text, created_at)
    VALUES (?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        item_id,
        text,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    add_coin(2)


def fetch_grouped():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM library ORDER BY title ASC")
    rows = c.fetchall()

    conn.close()

    data = {}

    for genre in GENRES:
        data[genre] = []

    for row in rows:
        genre = row["genre"] or "その他"

        if genre not in data:
            data[genre] = []

        data[genre].append(row)

    return data


def fetch_by_genre(genre):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM library
    WHERE genre = ?
    ORDER BY title ASC
    """, (genre,))

    rows = c.fetchall()

    conn.close()
    return rows


def fetch_item(item_id):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM library WHERE id = ?", (item_id,))
    item = c.fetchone()

    conn.close()
    return item


def fetch_reviews(item_id):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM reviews
    WHERE library_id = ?
    ORDER BY created_at DESC
    """, (item_id,))

    rows = c.fetchall()

    conn.close()
    return rows