import json
import os


THEME_FILE = "data/themes.json"


def load_themes():
    if not os.path.exists(THEME_FILE):
        return []

    with open(THEME_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def find_theme(theme_class):
    for theme in load_themes():
        if theme.get("class") == theme_class:
            return theme

    return None


def owned_themes():
    return [
        theme.get("class")
        for theme in load_themes()
    ]


def is_owned(theme_class):
    return theme_class in owned_themes()