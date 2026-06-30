from modules.database import connect


PREFECTURES = [
    "北海道",
    "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県", "三重県",
    "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]


STATUS_OPTIONS = {
    "none": {"label": "未訪問", "icon": "⬜", "class": "jp-none"},
    "passed": {"label": "通過した", "icon": "🚄", "class": "jp-passed"},
    "visited": {"label": "遊んだ", "icon": "🎒", "class": "jp-visited"},
    "stayed": {"label": "泊まった", "icon": "🛏", "class": "jp-stayed"},
    "lived": {"label": "住んだ", "icon": "🏠", "class": "jp-lived"}
}


def ensure_prefectures():
    conn = connect()
    c = conn.cursor()

    for name in PREFECTURES:
        c.execute("""
        INSERT OR IGNORE INTO prefectures
        (name, status)
        VALUES (?, 'none')
        """, (name,))

    conn.commit()
    conn.close()


def fetch_prefectures():
    ensure_prefectures()

    conn = connect()
    c = conn.cursor()

    rows = c.execute("""
    SELECT *
    FROM prefectures
    ORDER BY id ASC
    """).fetchall()

    conn.close()
    return rows


def update_prefecture(name, status):
    if status not in STATUS_OPTIONS:
        status = "none"

    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE prefectures
    SET status = ?
    WHERE name = ?
    """, (status, name))

    conn.commit()
    conn.close()


def japan_progress():
    rows = fetch_prefectures()

    visited = [
        row for row in rows
        if row["status"] != "none"
    ]

    return {
        "visited": len(visited),
        "total": 47,
        "percent": int((len(visited) / 47) * 100)
    }


def status_data(status):
    return STATUS_OPTIONS.get(status, STATUS_OPTIONS["none"])