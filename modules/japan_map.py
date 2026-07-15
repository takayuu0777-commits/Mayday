from modules.database import connect, is_postgres


PREFECTURES = [
    "北海道",
    "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県", "三重県",
    "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県",
    "鹿児島県", "沖縄県"
]


STATUS_OPTIONS = {
    "none": {
        "label": "未訪問",
        "icon": "⬜",
        "class": "jp-none"
    },
    "passed": {
        "label": "通過した",
        "icon": "🚄",
        "class": "jp-passed"
    },
    "visited": {
        "label": "遊んだ",
        "icon": "🎒",
        "class": "jp-visited"
    },
    "stayed": {
        "label": "泊まった",
        "icon": "🛏",
        "class": "jp-stayed"
    },
    "lived": {
        "label": "住んだ",
        "icon": "🏠",
        "class": "jp-lived"
    }
}


_prefectures_initialized = False
_prefecture_cache = None


def ensure_prefectures():
    global _prefectures_initialized

    if _prefectures_initialized:
        return

    conn = connect()
    c = conn.cursor()

    for name in PREFECTURES:
        if is_postgres():
            c.execute("""
            INSERT INTO prefectures
            (name, status)
            VALUES (?, 'none')
            ON CONFLICT (name) DO NOTHING
            """, (name,))
        else:
            c.execute("""
            INSERT OR IGNORE INTO prefectures
            (name, status)
            VALUES (?, 'none')
            """, (name,))

    conn.commit()
    conn.close()

    _prefectures_initialized = True


def fetch_prefectures(force_refresh=False):
    global _prefecture_cache

    ensure_prefectures()

    if _prefecture_cache is not None and not force_refresh:
        return _prefecture_cache

    conn = connect()
    c = conn.cursor()

    rows = c.execute("""
    SELECT *
    FROM prefectures
    ORDER BY id ASC
    """).fetchall()

    conn.close()

    _prefecture_cache = [dict(row) for row in rows]

    return _prefecture_cache


def update_prefecture(name, status):
    global _prefecture_cache

    if status not in STATUS_OPTIONS:
        status = "none"

    if name not in PREFECTURES:
        return False

    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE prefectures
    SET status = ?
    WHERE name = ?
    """, (status, name))

    conn.commit()
    conn.close()

    _prefecture_cache = None

    return True


def japan_progress(rows=None):
    if rows is None:
        rows = fetch_prefectures()

    visited_count = sum(
        1
        for row in rows
        if row["status"] != "none"
    )

    total = len(PREFECTURES)

    return {
        "visited": visited_count,
        "total": total,
        "percent": int((visited_count / total) * 100)
    }


def status_data(status):
    return STATUS_OPTIONS.get(
        status,
        STATUS_OPTIONS["none"]
    )