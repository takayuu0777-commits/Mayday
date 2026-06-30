from modules.database import connect
from modules.stats import life_stats


def basic_statistics():
    stats = life_stats()

    return [
        {"label": "記録", "value": stats["logs"], "icon": "📝"},
        {"label": "Library", "value": stats["library"], "icon": "📚"},
        {"label": "実績", "value": stats["achievements"], "icon": "🏆"},
        {"label": "ログイン", "value": stats["login"], "icon": "📅"}
    ]


def library_statistics():
    stats = life_stats()

    return [
        {"label": "映画", "value": stats.get("genre_映画", 0), "icon": "🎬"},
        {"label": "アニメ", "value": stats.get("genre_アニメ", 0), "icon": "📺"},
        {"label": "漫画", "value": stats.get("genre_漫画", 0), "icon": "📖"},
        {"label": "ゲーム", "value": stats.get("genre_ゲーム", 0), "icon": "🎮"},
        {"label": "小説", "value": stats.get("genre_小説", 0), "icon": "📚"}
    ]


def todo_statistics():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) AS count FROM todos WHERE done = 1")
    done = c.fetchone()["count"]

    c.execute("SELECT COUNT(*) AS count FROM todos WHERE done = 0")
    active = c.fetchone()["count"]

    conn.close()

    return {
        "done": done,
        "active": active
    }
