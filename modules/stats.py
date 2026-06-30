from modules.database import connect


def count_table(table):
    conn = connect()
    c = conn.cursor()

    c.execute(f"SELECT COUNT(*) AS count FROM {table}")
    row = c.fetchone()

    conn.close()
    return row["count"]


def done_goals_count():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) AS count FROM goals WHERE done = 1")
    row = c.fetchone()

    conn.close()
    return row["count"]


def category_counts():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT category, COUNT(*) AS count
    FROM logs
    GROUP BY category
    ORDER BY count DESC
    """)

    rows = c.fetchall()
    conn.close()
    return rows


def latest_shopping(limit=3):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM shopping
    WHERE done = 0
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()
    return rows


def genre_count(genre):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT COUNT(*) AS count
    FROM library
    WHERE genre = ?
    """, (genre,))

    row = c.fetchone()
    conn.close()
    return row["count"]


def life_stats():
    genres = {}

    for genre in [
        "映画",
        "アニメ",
        "漫画",
        "ゲーム",
        "小説",
        "ドラマ",
        "音楽",
        "舞台"
    ]:
        genres[f"genre_{genre}"] = genre_count(genre)

    return {
        "logs": count_table("logs"),
        "library": count_table("library"),
        "reviews": count_table("reviews"),
        "goals": count_table("goals"),
        "done_goals": done_goals_count(),
        "shopping": count_table("shopping"),
        "achievements": count_table("achievements_unlocked"),
        "login": count_table("login_days"),
        "categories": category_counts(),
        "latest_shopping": latest_shopping(),
        **genres
    }