import json
import os

from modules.database import connect


def load_json(path, fallback):
    if not os.path.exists(path):
        return fallback

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_titles():
    return load_json("data/titles.json", ["無称号"])


def load_icons():
    return load_json("data/icons.json", ["✦"])


def load_backgrounds():
    return load_json("data/backgrounds.json", [])


def get_profile():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM profile WHERE id = 1")
    row = c.fetchone()

    conn.close()
    return dict(row)


def update_profile(title, icon, background, bio):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE profile
    SET title = ?,
        icon = ?,
        background = ?,
        bio = ?
    WHERE id = 1
    """, (
        title,
        icon,
        background,
        bio
    ))

    conn.commit()
    conn.close()