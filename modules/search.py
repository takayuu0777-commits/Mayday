from modules.database import connect


def search_logs(keyword):
    conn = connect()
    c = conn.cursor()

    c.execute(
        """
        SELECT *
        FROM logs
        WHERE text LIKE ?
        ORDER BY created_at DESC
        """,
        (f"%{keyword}%",)
    )

    rows = c.fetchall()

    conn.close()

    return [dict(row) for row in rows]