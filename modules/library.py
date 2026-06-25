from modules.database import connect


def fetch_grouped():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM library ORDER BY title ASC")
    rows = c.fetchall()

    conn.close()

    data = {}

    for row in rows:
        genre = row["genre"] or "その他"
        data.setdefault(genre, []).append(row["title"])

    for genre in data:
        data[genre].sort()

    return data


def count_all():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) AS count FROM library")
    row = c.fetchone()

    conn.close()

    return row["count"]