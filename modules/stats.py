from modules.database import connect


def log_count():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) AS count FROM logs")
    count = c.fetchone()["count"]

    conn.close()
    return count


def library_count():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) AS count FROM library")
    count = c.fetchone()["count"]

    conn.close()
    return count


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


def life_stats():
    categories = category_count()

    return {
        "logs": log_count(),
        "library": library_count(),
        "thought": categories.get("思考", 0),
        "study": categories.get("学習", 0),
        "media": categories.get("メディア", 0),
        "work": categories.get("仕事", 0),
        "shopping": categories.get("買い物", 0),
        "goal": categories.get("目標", 0),
        "categories": category_count_list()
    }