from modules.database import connect


def profile_data():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM profile WHERE id = 1")
    profile = c.fetchone()

    conn.close()
    return dict(profile)


def count_table(table):
    conn = connect()
    c = conn.cursor()

    c.execute(f"SELECT COUNT(*) AS count FROM {table}")
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


def latest_goals(limit=3):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM goals
    WHERE done = 0
    ORDER BY created_at DESC
    LIMIT ?
    """, (limit,))

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


def life_stats():
    return {
        "logs": count_table("logs"),
        "library": count_table("library"),
        "reviews": count_table("reviews"),
        "goals": count_table("goals"),
        "shopping": count_table("shopping"),
        "achievements": count_table("achievements_unlocked"),
        "login": count_table("login_days"),
        "categories": category_counts(),
        "latest_goals": latest_goals(),
        "latest_shopping": latest_shopping()
    }