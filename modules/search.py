from modules.database import connect


def search_logs(user_id, keyword):
    if not user_id:
        return []

    keyword = (keyword or "").strip()

    conn = connect()
    c = conn.cursor()

    if keyword:
        c.execute("""
        SELECT *
        FROM logs
        WHERE user_id = ?
        AND (
            text LIKE ?
            OR summary LIKE ?
            OR category LIKE ?
        )
        ORDER BY created_at DESC
        """, (
            user_id,
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ))
    else:
        c.execute("""
        SELECT *
        FROM logs
        WHERE user_id = ?
        ORDER BY created_at DESC
        """, (user_id,))

    rows = c.fetchall()

    conn.close()

    return rows