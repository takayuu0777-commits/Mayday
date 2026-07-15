import json
import os

from modules.database import connect


_profile_table_ready = False


def load_json(path, fallback):
    if not os.path.exists(path):
        return fallback

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_titles():
    return load_json(
        "data/titles.json",
        ["無称号"]
    )


def load_icons():
    return load_json(
        "data/icons.json",
        ["✦"]
    )


def load_backgrounds():
    return load_json(
        "data/backgrounds.json",
        []
    )


def ensure_profile_table():
    global _profile_table_ready

    if _profile_table_ready:
        return

    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        user_id TEXT PRIMARY KEY,
        title TEXT DEFAULT '無称号',
        icon TEXT DEFAULT '✦',
        background TEXT DEFAULT 'default',
        bio TEXT DEFAULT '',
        coins INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

    _profile_table_ready = True


def ensure_profile(user_id):
    if not user_id:
        return False

    ensure_profile_table()

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT user_id
    FROM user_profiles
    WHERE user_id = ?
    """, (user_id,))

    existing = c.fetchone()

    if not existing:
        c.execute("""
        INSERT INTO user_profiles
        (
            user_id,
            title,
            icon,
            background,
            bio,
            coins
        )
        VALUES (?, '無称号', '✦', 'default', '', 0)
        """, (user_id,))

    conn.commit()
    conn.close()

    return True


def get_profile(user_id):
    if not user_id:
        return {
            "user_id": None,
            "title": "無称号",
            "icon": "✦",
            "background": "default",
            "bio": "",
            "coins": 0
        }

    ensure_profile(user_id)

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM user_profiles
    WHERE user_id = ?
    """, (user_id,))

    row = c.fetchone()
    conn.close()

    if not row:
        return {
            "user_id": user_id,
            "title": "無称号",
            "icon": "✦",
            "background": "default",
            "bio": "",
            "coins": 0
        }

    return dict(row)


def update_profile(
    user_id,
    title,
    icon,
    background,
    bio
):
    if not user_id:
        return False

    ensure_profile(user_id)

    clean_title = (title or "無称号").strip()
    clean_icon = (icon or "✦").strip()
    clean_background = (
        background or "default"
    ).strip()
    clean_bio = (bio or "").strip()

    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE user_profiles
    SET
        title = ?,
        icon = ?,
        background = ?,
        bio = ?
    WHERE user_id = ?
    """, (
        clean_title,
        clean_icon,
        clean_background,
        clean_bio,
        user_id
    ))

    conn.commit()
    conn.close()

    return True