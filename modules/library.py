import uuid
from datetime import datetime
from modules.database import connect


GENRES = [
    "アニメ",
    "漫画",
    "映画",
    "ゲーム",
    "小説",
    "ドラマ",
    "音楽",
    "舞台",
    "その他"
]


def normalize_genre(genre):
    if genre in GENRES:
        return genre
    return "その他"


def safe_rating(value):
    try:
        rating = int(value)
    except Exception:
        return 0

    if rating < 0:
        return 0

    if rating > 5:
        return 5

    return rating


def add_coin(amount):
    conn = connect()
    c = conn.cursor()

    c.execute(
        "UPDATE profile SET coins = coins + ? WHERE id = 1",
        (amount,)
    )

    conn.commit()
    conn.close()


def add_item(title, genre="その他", rating=0, review=""):
    title = (title or "").strip()
    genre = normalize_genre(genre)
    rating = safe_rating(rating)
    review = (review or "").strip()

    if not title:
        return None

    item_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO library
    (id, title, genre, rating, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        item_id,
        title,
        genre,
        rating,
        now
    ))

    if review:
        c.execute("""
        INSERT INTO reviews
        (id, library_id, text, created_at)
        VALUES (?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            item_id,
            review,
            now
        ))

    conn.commit()
    conn.close()

    add_coin(2)

    return item_id


def update_item(item_id, title, genre, rating):
    title = (title or "").strip()
    genre = normalize_genre(genre)
    rating = safe_rating(rating)

    if not title:
        return

    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE library
    SET title = ?,
        genre = ?,
        rating = ?
    WHERE id = ?
    """, (
        title,
        genre,
        rating,
        item_id
    ))

    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = connect()
    c = conn.cursor()

    c.execute("DELETE FROM reviews WHERE library_id = ?", (item_id,))
    c.execute("DELETE FROM library WHERE id = ?", (item_id,))

    conn.commit()
    conn.close()


def add_review(item_id, text, rating=None):
    text = (text or "").strip()
    rating = safe_rating(rating)

    if not text:
        return

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

    c.execute("""
    UPDATE library
    SET rating = ?
    WHERE id = ?
    """, (
        rating,
        item_id
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
        genre = normalize_genre(row["genre"])
        data[genre].append(row)

    return data


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