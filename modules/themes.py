import json
import os

from modules.database import connect


THEME_FILE = os.path.join(os.getcwd(), "data", "themes.json")

FREE_THEMES = [
    "dream",
    "deep"
]


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
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS owned_themes (
        theme_class TEXT PRIMARY KEY,
        purchased_at TEXT
    )
    """)

    rows = c.execute("SELECT theme_class FROM owned_themes").fetchall()

    conn.close()

    owned = [row["theme_class"] for row in rows]

    for theme in FREE_THEMES:
        if theme not in owned:
            owned.append(theme)

    return owned


def is_owned(theme_class):
    return theme_class in owned_themes()


def buy_theme(theme_class):
    theme = find_theme(theme_class)

    if not theme:
        return False, "テーマが見つかりません。"

    if is_owned(theme_class):
        return False, "すでに持っています。"

    price = int(theme.get("price", 0))

    conn = connect()
    c = conn.cursor()

    c.execute("SELECT coins FROM profile WHERE id = 1")
    profile = c.fetchone()

    if not profile or profile["coins"] < price:
        conn.close()
        return False, "コインが足りません。"

    c.execute("""
    UPDATE profile
    SET coins = coins - ?
    WHERE id = 1
    """, (price,))

    c.execute("""
    INSERT INTO owned_themes
    (theme_class, purchased_at)
    VALUES (?, datetime('now'))
    """, (theme_class,))

    conn.commit()
    conn.close()

    return True, "購入しました。"