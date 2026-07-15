from modules.database import connect


def fetch_statistics():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT COUNT(*) AS count
    FROM logs
    """)
    logs_count = c.fetchone()["count"]

    c.execute("""
    SELECT COUNT(*) AS count
    FROM library
    """)
    library_count = c.fetchone()["count"]

    c.execute("""
    SELECT COUNT(*) AS count
    FROM achievements_unlocked
    """)
    achievements_count = c.fetchone()["count"]

    c.execute("""
    SELECT COUNT(*) AS count
    FROM login_days
    """)
    login_count = c.fetchone()["count"]

    c.execute("""
    SELECT genre, COUNT(*) AS count
    FROM library
    GROUP BY genre
    """)
    genre_rows = c.fetchall()

    c.execute("""
    SELECT
        SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) AS done,
        SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END) AS active,
        COUNT(*) AS total
    FROM todos
    """)
    todo_row = c.fetchone()

    c.execute("""
    SELECT
        category,
        COUNT(*) AS count
    FROM logs
    GROUP BY category
    ORDER BY count DESC
    """)
    category_rows = c.fetchall()

    conn.close()

    genres = {
        row["genre"]: row["count"]
        for row in genre_rows
        if row["genre"]
    }

    categories = [
        {
            "name": row["category"] or "その他",
            "count": row["count"]
        }
        for row in category_rows
    ]

    todo_done = todo_row["done"] or 0
    todo_active = todo_row["active"] or 0
    todo_total = todo_row["total"] or 0

    todo_percent = 0

    if todo_total > 0:
        todo_percent = int((todo_done / todo_total) * 100)

    return {
        "basic_stats": [
            {
                "label": "人生ログ",
                "value": logs_count,
                "icon": "📝"
            },
            {
                "label": "Library",
                "value": library_count,
                "icon": "📚"
            },
            {
                "label": "実績",
                "value": achievements_count,
                "icon": "🏆"
            },
            {
                "label": "ログイン",
                "value": login_count,
                "icon": "📅"
            }
        ],

        "library_stats": [
            {
                "label": "映画",
                "value": genres.get("映画", 0),
                "icon": "🎬"
            },
            {
                "label": "アニメ",
                "value": genres.get("アニメ", 0),
                "icon": "📺"
            },
            {
                "label": "漫画",
                "value": genres.get("漫画", 0),
                "icon": "📖"
            },
            {
                "label": "ゲーム",
                "value": genres.get("ゲーム", 0),
                "icon": "🎮"
            },
            {
                "label": "小説",
                "value": genres.get("小説", 0),
                "icon": "📚"
            }
        ],

        "todo_stats": {
            "done": todo_done,
            "active": todo_active,
            "total": todo_total,
            "percent": todo_percent
        },

        "category_stats": categories[:6]
    }


def basic_statistics():
    return fetch_statistics()["basic_stats"]


def library_statistics():
    return fetch_statistics()["library_stats"]


def todo_statistics():
    return fetch_statistics()["todo_stats"]