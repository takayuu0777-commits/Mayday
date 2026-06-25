import json
import os

from modules.stats import life_stats


ACHIEVEMENT_FILE = os.path.join(os.getcwd(), "data", "achievements.json")


def load_achievements():
    if not os.path.exists(ACHIEVEMENT_FILE):
        return []

    with open(ACHIEVEMENT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


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


def target_value(achievement_id):
    numbers = ""

    for char in achievement_id:
        if char.isdigit():
            numbers += char

    if numbers:
        return int(numbers)

    return 1


def achievement_progress(achievement):
    current = progress_value(achievement["id"])
    target = target_value(achievement["id"])

    if current > target:
        current = target

    percent = int((current / target) * 100) if target > 0 else 0

    return {
        "current": current,
        "target": target,
        "percent": percent,
        "unlocked": current >= target
    }


def all_achievements():
    result = []

    for achievement in load_achievements():
        progress = achievement_progress(achievement)

        item = dict(achievement)
        item["progress"] = progress

        result.append(item)

    return result


def find_achievement(achievement_id):
    for achievement in all_achievements():
        if achievement["id"] == achievement_id:
            return achievement

    return None