from modules.database import connect
from modules.stats import life_stats


def fetch_statistics(user_id):
    if not user_id:
        return {
            "basic_stats": [],
            "library_stats": [],
            "todo_stats": {
                "done": 0,
                "active": 0,
                "total": 0,
                "percent": 0
            },
            "category_stats": []
        }

    stats = life_stats(user_id)

    conn = connect()
    c = conn.cursor()

    try:
        c.execute("""
        SELECT
            SUM(
                CASE WHEN done = 1
                THEN 1 ELSE 0 END
            ) AS done,
            SUM(
                CASE WHEN done = 0
                THEN 1 ELSE 0 END
            ) AS active,
            COUNT(*) AS total
        FROM todos
        WHERE user_id = ?
        """, (user_id,))

        todo_row = c.fetchone()

        c.execute("""
        SELECT
            category,
            COUNT(*) AS count
        FROM logs
        WHERE user_id = ?
        GROUP BY category
        ORDER BY count DESC
        LIMIT 6
        """, (user_id,))

        category_rows = c.fetchall()

    finally:
        conn.close()

    todo_done = (
        todo_row["done"] or 0
        if todo_row
        else 0
    )

    todo_active = (
        todo_row["active"] or 0
        if todo_row
        else 0
    )

    todo_total = (
        todo_row["total"] or 0
        if todo_row
        else 0
    )

    todo_percent = 0

    if todo_total > 0:
        todo_percent = int(
            (todo_done / todo_total) * 100
        )

    category_stats = [
        {
            "name": row["category"] or "その他",
            "count": row["count"] or 0
        }
        for row in category_rows
    ]

    return {
        "basic_stats": [
            {
                "label": "人生ログ",
                "value": stats.get("logs", 0),
                "icon": "📝"
            },
            {
                "label": "Library",
                "value": stats.get("library", 0),
                "icon": "📚"
            },
            {
                "label": "実績",
                "value": stats.get(
                    "achievements",
                    0
                ),
                "icon": "🏆"
            },
            {
                "label": "ログイン",
                "value": stats.get("login", 0),
                "icon": "📅"
            }
        ],

        "library_stats": [
            {
                "label": "映画",
                "value": stats.get(
                    "genre_映画",
                    0
                ),
                "icon": "🎬"
            },
            {
                "label": "アニメ",
                "value": stats.get(
                    "genre_アニメ",
                    0
                ),
                "icon": "📺"
            },
            {
                "label": "漫画",
                "value": stats.get(
                    "genre_漫画",
                    0
                ),
                "icon": "📖"
            },
            {
                "label": "ゲーム",
                "value": stats.get(
                    "genre_ゲーム",
                    0
                ),
                "icon": "🎮"
            },
            {
                "label": "小説",
                "value": stats.get(
                    "genre_小説",
                    0
                ),
                "icon": "📚"
            }
        ],

        "todo_stats": {
            "done": todo_done,
            "active": todo_active,
            "total": todo_total,
            "percent": todo_percent
        },

        "category_stats": category_stats
    }