import json
import os


FILE_PATH = "data/life_categories.json"


def load_categories():
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_categories(categories):
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(categories, file, ensure_ascii=False, indent=4)


def update_categories(form):
    categories = load_categories()

    for category in categories:
        category["enabled"] = category["id"] in form

    save_categories(categories)


def enabled_categories():
    return [
        category
        for category in load_categories()
        if category.get("enabled")
    ]