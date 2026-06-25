from modules.database import connect


def fetch_data():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT date_key, category
    FROM logs
    """)

    rows = c.fetchall()

    conn.close()

    data = {}

    for row in rows:
        date = row["date_key"]
        category = row["category"]

        data.setdefault(date, {})
        data[date][category] = data[date].get(category, 0) + 1

    return data