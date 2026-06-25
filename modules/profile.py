from modules.database import connect


DEFAULT_TITLES = [
    "無称号",
    "はじまりの記録者",
    "作品収集家",
    "思索家",
    "探究者",
    "Second Brain Explorer",
    "人生収集家",
    "記録魔"
]


def get_profile():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM profile WHERE id = 1")
    row = c.fetchone()

    conn.close()

    return dict(row)


def available_titles():
    return DEFAULT_TITLES


def update_title(title):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE profile
    SET title = ?
    WHERE id = 1
    """, (title,))

    conn.commit()
    conn.close()