import json
import os
from datetime import datetime

from modules.database import connect, is_postgres
from modules.stats import life_stats


ACHIEVEMENT_FILE = "data/achievements.json"


_achievement_table_ready = False


def load_achievements():
    if not os.path.exists(ACHIEVEMENT_FILE):
        return []

    try:
        with open(
            ACHIEVEMENT_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (
        OSError,
        json.JSONDecodeError
    ):
        pass

    return []


def ensure_table():
    """
    複数ユーザー専用の実績解除テーブルを準備します。
    """
    global _achievement_table_ready

    if _achievement_table_ready:
        return

    conn = connect()

    try:
        c = conn.cursor()

        if is_postgres():
            c.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at TEXT NOT NULL,
                UNIQUE (
                    user_id,
                    achievement_id
                )
            )
            """)

        else:
            c.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at TEXT NOT NULL,
                UNIQUE (
                    user_id,
                    achievement_id
                )
            )
            """)

        conn.commit()
        _achievement_table_ready = True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def unlocked_ids(user_id):
    """
    指定ユーザーが解除した実績IDを取得します。
    """
    if not user_id:
        return []

    ensure_table()

    conn = connect()

    try:
        c = conn.cursor()

        c.execute("""
        SELECT achievement_id
        FROM user_achievements
        WHERE user_id = ?
        ORDER BY unlocked_at ASC
        """, (user_id,))

        rows = c.fetchall()

    finally:
        conn.close()

    return [
        row["achievement_id"]
        for row in rows
    ]


def achievement_progress(
    user_id,
    achievement,
    stats=None
):
    """
    指定ユーザーの実績進捗を計算します。
    """
    if stats is None:
        stats = life_stats(user_id)

    stat_name = achievement.get("stat")
    target = achievement.get("target", 1)

    try:
        target = int(target)
    except (TypeError, ValueError):
        target = 1

    try:
        current = int(
            stats.get(stat_name, 0)
        )
    except (TypeError, ValueError):
        current = 0

    if target < 1:
        target = 1

    display_current = min(
        current,
        target
    )

    percent = int(
        (display_current / target) * 100
    )

    return {
        "current": display_current,
        "actual_current": current,
        "target": target,
        "percent": min(percent, 100),
        "unlocked": current >= target
    }


def unlock_achievement(
    user_id,
    achievement_id
):
    """
    指定ユーザーの実績を解除します。
    すでに解除済みなら何もしません。
    """
    if not user_id or not achievement_id:
        return False

    ensure_table()

    conn = connect()

    try:
        c = conn.cursor()

        if is_postgres():
            c.execute("""
            INSERT INTO user_achievements
            (
                user_id,
                achievement_id,
                unlocked_at
            )
            VALUES (?, ?, ?)
            ON CONFLICT (
                user_id,
                achievement_id
            )
            DO NOTHING
            """, (
                user_id,
                achievement_id,
                datetime.now().isoformat()
            ))

        else:
            c.execute("""
            INSERT OR IGNORE INTO user_achievements
            (
                user_id,
                achievement_id,
                unlocked_at
            )
            VALUES (?, ?, ?)
            """, (
                user_id,
                achievement_id,
                datetime.now().isoformat()
            ))

        inserted = c.rowcount == 1

        conn.commit()

        return inserted

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def sync_achievements(user_id):
    """
    条件を達成した実績を自動解除します。
    """
    if not user_id:
        return []

    achievements = load_achievements()
    stats = life_stats(user_id)

    newly_unlocked = []

    for achievement in achievements:
        achievement_id = achievement.get("id")

        if not achievement_id:
            continue

        progress = achievement_progress(
            user_id,
            achievement,
            stats
        )

        if not progress["unlocked"]:
            continue

        inserted = unlock_achievement(
            user_id,
            achievement_id
        )

        if inserted:
            newly_unlocked.append(
                achievement_id
            )

    return newly_unlocked


def all_achievements(user_id):
    """
    指定ユーザーの全実績と進捗を返します。
    """
    if not user_id:
        return []

    sync_achievements(user_id)

    unlocked = set(
        unlocked_ids(user_id)
    )

    stats = life_stats(user_id)
    result = []

    for achievement in load_achievements():
        item = dict(achievement)

        item["progress"] = (
            achievement_progress(
                user_id,
                achievement,
                stats
            )
        )

        item["unlocked"] = (
            item.get("id") in unlocked
        )

        result.append(item)

    return result


def compact_categories(user_id):
    """
    実績カテゴリごとの解除数を返します。
    """
    categories = {
        "アプリ": {
            "name": "アプリ",
            "icon": "✦",
            "total": 0,
            "unlocked": 0
        },
        "作品": {
            "name": "作品",
            "icon": "📚",
            "total": 0,
            "unlocked": 0
        },
        "人生": {
            "name": "人生",
            "icon": "🌍",
            "total": 0,
            "unlocked": 0
        },
        "特別": {
            "name": "特別",
            "icon": "⭐",
            "total": 0,
            "unlocked": 0
        }
    }

    for achievement in all_achievements(
        user_id
    ):
        group = achievement.get(
            "group",
            "アプリ"
        )

        if group not in categories:
            group = "アプリ"

        categories[group]["total"] += 1

        if achievement["unlocked"]:
            categories[group]["unlocked"] += 1

    return list(
        categories.values()
    )


def achievements_by_group(
    user_id,
    group
):
    """
    指定カテゴリの実績だけを返します。
    """
    return [
        achievement
        for achievement in all_achievements(
            user_id
        )
        if achievement.get(
            "group",
            "アプリ"
        ) == group
    ]


def find_achievement(
    user_id,
    achievement_id
):
    """
    指定ユーザー用の実績詳細を返します。
    """
    if not user_id or not achievement_id:
        return None

    for achievement in all_achievements(
        user_id
    ):
        if achievement.get("id") == achievement_id:
            return achievement

    return None


def unlocked_count(user_id):
    """
    指定ユーザーの解除済み実績数を返します。
    """
    return len(
        unlocked_ids(user_id)
    )