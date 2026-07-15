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
    except (TypeError, ValueError):
        return 0

    return max(0, min(5, rating))


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


def add_item(
    user_id,
    title,
    genre="その他",
    rating=0,
    review=""
):
    clean_title = (title or "").strip()
    clean_genre = normalize_genre(genre)
    clean_rating = safe_rating(rating)
    clean_review = (review or "").strip()

    if not user_id or not clean_title:
        return None

    item_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO library
    (
        id,
        user_id,
        title,
        genre,
        rating,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        item_id,
        user_id,
        clean_title,
        clean_genre,
        clean_rating,
        now
    ))

    if clean_review:
        c.execute("""
        INSERT INTO reviews
        (
            id,
            user_id,
            library_id,
            text,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            user_id,
            item_id,
            clean_review,
            now
        ))

    conn.commit()
    conn.close()

    add_coin(user_id, 2)

    return item_id


def update_item(
    user_id,
    item_id,
    title,
    genre,
    rating,
    review=None
):
    clean_title = (title or "").strip()
    clean_genre = normalize_genre(genre)
    clean_rating = safe_rating(rating)

    if not user_id or not item_id or not clean_title:
        return False

    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE library
    SET
        title = ?,
        genre = ?,
        rating = ?
    WHERE id = ?
      AND user_id = ?
    """, (
        clean_title,
        clean_genre,
        clean_rating,
        item_id,
        user_id
    ))

    if c.rowcount != 1:
        conn.rollback()
        conn.close()
        return False

    if review is not None:
        clean_review = (review or "").strip()

        c.execute("""
        SELECT id
        FROM reviews
        WHERE library_id = ?
          AND user_id = ?
        ORDER BY created_at DESC
        """, (
            item_id,
            user_id
        ))

        review_rows = c.fetchall()

        if clean_review:
            now = datetime.now().isoformat()

            if review_rows:
                main_review_id = review_rows[0]["id"]

                c.execute("""
                UPDATE reviews
                SET
                    text = ?,
                    created_at = ?
                WHERE id = ?
                  AND user_id = ?
                """, (
                    clean_review,
                    now,
                    main_review_id,
                    user_id
                ))

                for old_review in review_rows[1:]:
                    c.execute("""
                    DELETE FROM reviews
                    WHERE id = ?
                      AND user_id = ?
                    """, (
                        old_review["id"],
                        user_id
                    ))

            else:
                c.execute("""
                INSERT INTO reviews
                (
                    id,
                    user_id,
                    library_id,
                    text,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    user_id,
                    item_id,
                    clean_review,
                    now
                ))

        else:
            c.execute("""
            DELETE FROM reviews
            WHERE library_id = ?
              AND user_id = ?
            """, (
                item_id,
                user_id
            ))

    conn.commit()
    conn.close()

    return True


def delete_item(user_id, item_id):
    if not user_id or not item_id:
        return False

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT id
    FROM library
    WHERE id = ?
      AND user_id = ?
    """, (
        item_id,
        user_id
    ))

    if not c.fetchone():
        conn.close()
        return False

    c.execute("""
    DELETE FROM reviews
    WHERE library_id = ?
      AND user_id = ?
    """, (
        item_id,
        user_id
    ))

    c.execute("""
    DELETE FROM library
    WHERE id = ?
      AND user_id = ?
    """, (
        item_id,
        user_id
    ))

    conn.commit()
    conn.close()

    return True


def add_review(user_id, item_id, text, rating=None):
    clean_text = (text or "").strip()

    if not user_id or not clean_text:
        return False

    current_item = fetch_item(user_id, item_id)

    if not current_item:
        return False

    selected_rating = (
        safe_rating(rating)
        if rating not in (None, "")
        else current_item["rating"]
    )

    result = update_item(
        user_id,
        item_id,
        current_item["title"],
        current_item["genre"],
        selected_rating,
        clean_text
    )

    if result:
        add_coin(user_id, 2)

    return result


def fetch_grouped(user_id):
    data = {
        genre: []
        for genre in GENRES
    }

    if not user_id:
        return data

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM library
    WHERE user_id = ?
    ORDER BY title ASC
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    for row in rows:
        genre = normalize_genre(row["genre"])
        data[genre].append(row)

    return data


def fetch_item(user_id, item_id):
    if not user_id or not item_id:
        return None

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM library
    WHERE id = ?
      AND user_id = ?
    """, (
        item_id,
        user_id
    ))

    item = c.fetchone()
    conn.close()

    return item


def fetch_review(user_id, item_id):
    if not user_id or not item_id:
        return None

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM reviews
    WHERE library_id = ?
      AND user_id = ?
    ORDER BY created_at DESC
    LIMIT 1
    """, (
        item_id,
        user_id
    ))

    review = c.fetchone()
    conn.close()

    return review


def fetch_reviews(user_id, item_id):
    review = fetch_review(user_id, item_id)

    if review:
        return [review]

    return []