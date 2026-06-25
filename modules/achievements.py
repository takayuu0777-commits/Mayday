import json
import os
from datetime import datetime

from modules.database import connect
from modules.stats import life_stats


ACHIEVEMENT_FILE = os.path.join(os.getcwd(), "data", "achievements.json")


def load_achievements():
    if not os.path.exists(ACHIEVEMENT_FILE):
        return []

    with open(ACHIEVEMENT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def unlocked_ids():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS achievements_unlocked (
        id TEXT PRIMARY KEY,
        unlocked_at TEXT
    )
    """)

    rows = c.execute("SELECT id FROM achievements_unlocked").fetchall()

    conn.close()

    return [row["id"] for row in rows]


def progress_value(achievement_id):
    stats = life_stats()

    if achievement_id.startswith("log"):
        return stats["logs"]

    if achievement_id.startswith("library"):
        return stats["library"]

    if achievement_id.startswith("goal"):
        return stats["goals"]

    if achievement_id.startswith("shopping"):
        return stats["shopping"]

    if achievement_id.startswith("login"):
        return stats["login"]

    if achievement_id.startswith("review"):
        return stats["reviews"]

    return 0


def achievement_progress(achievement):
    current = progress_value(achievement["id"])
    target = int(achievement.get("target", 1))

    if current > target:
        current = target

    percent = int((current / target) * 100) if target > 0 else 0

    return {
        "current": current,
        "target": target,
        "percent": percent,
        "unlocked": current >= target
    }


def sync_achievements():
    achievements = load_achievements()
    already = unlocked_ids()

    conn = connect()
    c = conn.cursor()

    reward_total = 0

    for achievement in achievements:
        progress = achievement_progress(achievement)

        if progress["unlocked"] and achievement["id"] not in already:
            c.execute("""
            INSERT INTO achievements_unlocked
            (id, unlocked_at)
            VALUES (?, ?)
            """, (
                achievement["id"],
                datetime.now().isoformat()
            ))

            reward_total += int(achievement.get("reward", 0))

    if reward_total > 0:
        c.execute("""
        UPDATE profile
        SET coins = coins + ?
        WHERE id = 1
        """, (reward_total,))

    conn.commit()
    conn.close()


def all_achievements():
    sync_achievements()

    unlocked = unlocked_ids()
    result = []

    for achievement in load_achievements():
        progress = achievement_progress(achievement)

        item = dict(achievement)
        item["progress"] = progress
        item["unlocked"] = achievement["id"] in unlocked

        result.append(item)

    return result


def find_achievement(achievement_id):
    for achievement in all_achievements():
        if achievement["id"] == achievement_id:
            return achievement

    return None


def unlocked_count():
    return len(unlocked_ids())