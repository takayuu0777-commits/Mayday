import json
import os
from datetime import datetime
from modules.database import connect
from modules.stats import life_stats


ACHIEVEMENT_FILE = os.path.join(os.getcwd(), "data", "achievements.json")


RANKS = [
    "銅",
    "銀",
    "金",
    "水晶",
    "サファイア",
    "ルビー",
    "エメラルド",
    "アメジスト",
    "プラチナ",
    "ダイヤ"
]


def load_achievements():
    if not os.path.exists(ACHIEVEMENT_FILE):
        return []

    with open(ACHIEVEMENT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def ensure_table():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS achievements_unlocked (
        id TEXT PRIMARY KEY,
        unlocked_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def unlocked_ids():
    ensure_table()

    conn = connect()
    c = conn.cursor()

    rows = c.execute("SELECT id FROM achievements_unlocked").fetchall()

    conn.close()

    return [row["id"] for row in rows]


def achievement_progress(achievement):
    stats = life_stats()
    stat = achievement.get("stat")
    target = int(achievement.get("target", 1))
    current = int(stats.get(stat, 0))

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
    ensure_table()

    achievements = load_achievements()
    already = unlocked_ids()

    conn = connect()
    c = conn.cursor()

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

    conn.commit()
    conn.close()


def all_achievements():
    sync_achievements()

    unlocked = unlocked_ids()
    result = []

    for achievement in load_achievements():
        item = dict(achievement)
        item["progress"] = achievement_progress(achievement)
        item["unlocked"] = item["id"] in unlocked
        result.append(item)

    return result


def achievement_categories():
    achievements = all_achievements()
    categories = {}

    for achievement in achievements:
        category = achievement["category"]

        if category not in categories:
            categories[category] = {
                "name": category,
                "total": 0,
                "unlocked": 0
            }

        categories[category]["total"] += 1

        if achievement["unlocked"]:
            categories[category]["unlocked"] += 1

    return list(categories.values())


def achievements_by_category(category):
    return [
        achievement
        for achievement in all_achievements()
        if achievement["category"] == category
    ]


def find_achievement(achievement_id):
    for achievement in all_achievements():
        if achievement["id"] == achievement_id:
            return achievement

    return None


def unlocked_count():
    return len(unlocked_ids())