import json
import os


THEME_FILE = os.path.join(os.getcwd(), "data", "themes.json")


def load_themes():
    """
    利用可能なテーマ一覧を取得
    """

    if not os.path.exists(THEME_FILE):
        return []

    with open(THEME_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_theme(theme_name):
    """
    名前からテーマ取得
    """

    for theme in load_themes():
        if theme["name"] == theme_name:
            return theme

    return None


def default_theme():
    """
    デフォルトテーマ
    """

    theme = get_theme("Dream")

    if theme:
        return theme

    themes = load_themes()

    if themes:
        return themes[0]

    return {
        "name": "Dream",
        "class": "dream",
        "price": 0
    }