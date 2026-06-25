from modules.database import connect


def count_table(table):
    conn = connect()
    c = conn.cursor()

    c.execute(f"SELECT COUNT(*) AS count FROM {table}")
    count = c.fetchone()["count"]

    conn.close()
    return count


def log_count():
    return count_table("logs")


def library_count():
    return count_table("library")


def review_count():
    return count_table("reviews")


def goal_count():
    return count_table("goals")


def shopping_count():
    return count_table("shopping")


def login_count():
    return count_table("login_days")


def achievement_count():
    return count_table("achievements_unlocked")


def category_count():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT category, COUNT(*) AS count
    FROM logs
    GROUP BY category
    """)

    rows = c.fetchall()
    conn.close()

    data = {}

    for row in rows:
        data[row["category"]] = row["count"]

    return data


def category_count_list():
    data = category_count()

    result = []

    for category, count in data.items():
        result.append({
            "category": category,
            "count": count
        })

    result.sort(key=lambda x: x["count"], reverse=True)

    return result


def profile_data():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM profile WHERE id = 1")
    row = c.fetchone()

    conn.close()

    return dict(row)


def life_stats():
    categories = category_count()

    return {
        "logs": log_count(),
        "library": library_count(),
        "reviews": review_count(),
        "goals": goal_count(),
        "shopping": shopping_count(),
        "login": login_count(),
        "achievements": achievement_count(),
        "thought": categories.get("思考", 0),
        "study": categories.get("学習", 0),
        "media": categories.get("メディア", 0),
        "work": categories.get("仕事", 0),
        "buy": categories.get("買い物", 0),
        "goal": categories.get("目標", 0),
        "categories": category_count_list()
    }