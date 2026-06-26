import json
import os

from modules.database import connect


TITLE_FILE = os.path.join("data", "titles.json")
ICON_FILE = os.path.join("data", "icons.json")


def load_titles():
    if not os.path.exists(TITLE_FILE):
        return ["無称号"]

    with open(TITLE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_icons():
    if not os.path.exists(ICON_FILE):
        return ["🧠"]

    with open(ICON_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_profile():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM profile WHERE id = 1")
    profile = c.fetchone()

    conn.close()

    return dict(profile)


def update_profile(title, icon):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE profile
    SET title = ?,
        icon = ?
    WHERE id = 1
    """, (
        title,
        icon
    ))

    conn.commit()
    conn.close()