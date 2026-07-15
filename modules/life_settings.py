from modules.database import connect, is_postgres


DEFAULT_CATEGORIES = [
    ("thinking", "💡", "思考"),
    ("study", "📚", "学習"),
    ("work", "💼", "仕事"),
    ("media", "🎬", "メディア"),
    ("people", "👥", "人"),
    ("place", "📍", "場所"),
    ("health", "💪", "健康"),
    ("shopping", "🛒", "買い物"),
    ("goal", "🎯", "目標"),
    ("achievement", "🏆", "実績"),
    ("other", "✦", "その他")
]


_table_ready = False
_initialized_users = set()


def ensure_table():
    global _table_ready

    if _table_ready:
        return

    conn = connect()

    try:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS user_categories (
            user_id TEXT NOT NULL,
            category_id TEXT NOT NULL,
            icon TEXT NOT NULL,
            name TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, category_id)
        )
        """)

        conn.commit()
        _table_ready = True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def ensure_categories(user_id):
    if not user_id:
        return False

    ensure_table()

    if user_id in _initialized_users:
        return True

    conn = connect()

    try:
        c = conn.cursor()

        for sort_order, category in enumerate(
            DEFAULT_CATEGORIES
        ):
            category_id, icon, name = category

            if is_postgres():
                c.execute("""
                INSERT INTO user_categories
                (
                    user_id,
                    category_id,
                    icon,
                    name,
                    enabled,
                    sort_order
                )
                VALUES (?, ?, ?, ?, 1, ?)
                ON CONFLICT (user_id, category_id)
                DO NOTHING
                """, (
                    user_id,
                    category_id,
                    icon,
                    name,
                    sort_order
                ))

            else:
                c.execute("""
                INSERT OR IGNORE INTO user_categories
                (
                    user_id,
                    category_id,
                    icon,
                    name,
                    enabled,
                    sort_order
                )
                VALUES (?, ?, ?, ?, 1, ?)
                """, (
                    user_id,
                    category_id,
                    icon,
                    name,
                    sort_order
                ))

        conn.commit()
        _initialized_users.add(user_id)

        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def load_categories(user_id):
    if not user_id:
        return []

    ensure_categories(user_id)

    conn = connect()

    try:
        c = conn.cursor()

        c.execute("""
        SELECT
            category_id AS id,
            icon,
            name,
            enabled,
            sort_order
        FROM user_categories
        WHERE user_id = ?
        ORDER BY sort_order ASC
        """, (user_id,))

        rows = c.fetchall()

    finally:
        conn.close()

    return [
        {
            "id": row["id"],
            "icon": row["icon"],
            "name": row["name"],
            "enabled": bool(row["enabled"])
        }
        for row in rows
    ]


def update_categories(user_id, form):
    if not user_id:
        return False

    ensure_categories(user_id)

    conn = connect()

    try:
        c = conn.cursor()

        for category_id, _, _ in DEFAULT_CATEGORIES:
            enabled = (
                1
                if category_id in form
                else 0
            )

            c.execute("""
            UPDATE user_categories
            SET enabled = ?
            WHERE user_id = ?
              AND category_id = ?
            """, (
                enabled,
                user_id,
                category_id
            ))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def enabled_categories(user_id):
    return [
        category
        for category in load_categories(user_id)
        if category["enabled"]
    ]