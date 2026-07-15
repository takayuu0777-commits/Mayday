from modules.database import connect, is_postgres


_extra_tables_ready = False


def ensure_multi_user_stat_tables():
    """
    複数ユーザー用のログイン日テーブルを準備します。
    実績テーブルも、まだ存在しない場合に作成します。
    """
    global _extra_tables_ready

    if _extra_tables_ready:
        return

    conn = connect()

    try:
        c = conn.cursor()

        if is_postgres():
            c.execute("""
            CREATE TABLE IF NOT EXISTS user_login_days (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                date_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (user_id, date_key)
            )
            """)

            c.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at TEXT NOT NULL,
                UNIQUE (user_id, achievement_id)
            )
            """)

        else:
            c.execute("""
            CREATE TABLE IF NOT EXISTS user_login_days (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (user_id, date_key)
            )
            """)

            c.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at TEXT NOT NULL,
                UNIQUE (user_id, achievement_id)
            )
            """)

        conn.commit()
        _extra_tables_ready = True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def count_rows(cursor, table_name, user_id):
    cursor.execute(
        f"""
        SELECT COUNT(*) AS count
        FROM {table_name}
        WHERE user_id = ?
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    if not row:
        return 0

    return row["count"] or 0


def life_stats(user_id):
    """
    ログイン中ユーザーだけの統計を取得します。
    """
    empty_stats = {
        "logs": 0,
        "library": 0,
        "goals": 0,
        "shopping": 0,
        "todos": 0,
        "achievements": 0,
        "login": 0,
        "genre_映画": 0,
        "genre_アニメ": 0,
        "genre_漫画": 0,
        "genre_ゲーム": 0,
        "genre_小説": 0
    }

    if not user_id:
        return empty_stats

    ensure_multi_user_stat_tables()

    conn = connect()

    try:
        c = conn.cursor()

        stats = {
            "logs": count_rows(
                c,
                "logs",
                user_id
            ),
            "library": count_rows(
                c,
                "library",
                user_id
            ),
            "goals": count_rows(
                c,
                "goals",
                user_id
            ),
            "shopping": count_rows(
                c,
                "shopping",
                user_id
            ),
            "todos": count_rows(
                c,
                "todos",
                user_id
            ),
            "achievements": count_rows(
                c,
                "user_achievements",
                user_id
            ),
            "login": count_rows(
                c,
                "user_login_days",
                user_id
            )
        }

        genres = [
            "映画",
            "アニメ",
            "漫画",
            "ゲーム",
            "小説"
        ]

        for genre in genres:
            c.execute("""
            SELECT COUNT(*) AS count
            FROM library
            WHERE user_id = ?
              AND genre = ?
            """, (
                user_id,
                genre
            ))

            row = c.fetchone()

            stats[f"genre_{genre}"] = (
                row["count"] if row else 0
            ) or 0

        return stats

    finally:
        conn.close()