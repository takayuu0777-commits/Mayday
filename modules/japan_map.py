from modules.database import connect, is_postgres


PREFECTURES = [
    "北海道",
    "青森県",
    "岩手県",
    "宮城県",
    "秋田県",
    "山形県",
    "福島県",
    "茨城県",
    "栃木県",
    "群馬県",
    "埼玉県",
    "千葉県",
    "東京都",
    "神奈川県",
    "新潟県",
    "富山県",
    "石川県",
    "福井県",
    "山梨県",
    "長野県",
    "岐阜県",
    "静岡県",
    "愛知県",
    "三重県",
    "滋賀県",
    "京都府",
    "大阪府",
    "兵庫県",
    "奈良県",
    "和歌山県",
    "鳥取県",
    "島根県",
    "岡山県",
    "広島県",
    "山口県",
    "徳島県",
    "香川県",
    "愛媛県",
    "高知県",
    "福岡県",
    "佐賀県",
    "長崎県",
    "熊本県",
    "大分県",
    "宮崎県",
    "鹿児島県",
    "沖縄県"
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


_table_initialized = False
_initialized_users = set()
_prefecture_cache = {}


def ensure_user_prefectures_table():
    """
    複数ユーザー専用の都道府県テーブルを作成します。

    既存のprefecturesテーブルは変更せず、
    user_prefecturesという新しいテーブルを使用します。
    """
    global _table_initialized

    if _table_initialized:
        return

    conn = connect()

    try:
        c = conn.cursor()

        if is_postgres():
            c.execute("""
            CREATE TABLE IF NOT EXISTS user_prefectures (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'none',
                UNIQUE (user_id, name)
            )
            """)

        else:
            c.execute("""
            CREATE TABLE IF NOT EXISTS user_prefectures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'none',
                UNIQUE (user_id, name)
            )
            """)

        conn.commit()
        _table_initialized = True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def ensure_prefectures(user_id):
    """
    指定ユーザー用の47都道府県データを準備します。
    """
    if not user_id:
        return False

    ensure_user_prefectures_table()

    if user_id in _initialized_users:
        return True

    conn = connect()

    try:
        c = conn.cursor()

        for name in PREFECTURES:
            if is_postgres():
                c.execute("""
                INSERT INTO user_prefectures
                (
                    user_id,
                    name,
                    status
                )
                VALUES (?, ?, 'none')
                ON CONFLICT (user_id, name)
                DO NOTHING
                """, (
                    user_id,
                    name
                ))

            else:
                c.execute("""
                INSERT OR IGNORE INTO user_prefectures
                (
                    user_id,
                    name,
                    status
                )
                VALUES (?, ?, 'none')
                """, (
                    user_id,
                    name
                ))

        conn.commit()
        _initialized_users.add(user_id)

        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def fetch_prefectures(user_id, force_refresh=False):
    """
    ログイン中ユーザーの都道府県データだけを取得します。
    """
    if not user_id:
        return []

    ensure_prefectures(user_id)

    if (
        not force_refresh
        and user_id in _prefecture_cache
    ):
        return _prefecture_cache[user_id]

    conn = connect()

    try:
        c = conn.cursor()

        c.execute("""
        SELECT
            id,
            name,
            status
        FROM user_prefectures
        WHERE user_id = ?
        """, (user_id,))

        rows = c.fetchall()

    finally:
        conn.close()

    rows_by_name = {}

    for row in rows:
        status = row["status"]

        if status not in STATUS_OPTIONS:
            status = "none"

        rows_by_name[row["name"]] = {
            "id": row["id"],
            "name": row["name"],
            "status": status
        }

    result = []

    for code, name in enumerate(
        PREFECTURES,
        start=1
    ):
        prefecture = rows_by_name.get(name)

        if not prefecture:
            continue

        prefecture["code"] = code
        prefecture["status_label"] = (
            STATUS_OPTIONS[prefecture["status"]]["label"]
        )
        prefecture["status_icon"] = (
            STATUS_OPTIONS[prefecture["status"]]["icon"]
        )
        prefecture["status_class"] = (
            STATUS_OPTIONS[prefecture["status"]]["class"]
        )

        result.append(prefecture)

    _prefecture_cache[user_id] = result

    return result


def update_prefecture(user_id, name, status):
    """
    指定ユーザーの都道府県状態だけを更新します。
    """
    if not user_id:
        return False

    if name not in PREFECTURES:
        return False

    if status not in STATUS_OPTIONS:
        status = "none"

    ensure_prefectures(user_id)

    conn = connect()

    try:
        c = conn.cursor()

        c.execute("""
        UPDATE user_prefectures
        SET status = ?
        WHERE user_id = ?
          AND name = ?
        """, (
            status,
            user_id,
            name
        ))

        updated = c.rowcount == 1

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    _prefecture_cache.pop(
        user_id,
        None
    )

    return updated


def japan_progress(user_id, rows=None):
    """
    指定ユーザーの日本制覇率を計算します。
    """
    if rows is None:
        rows = fetch_prefectures(user_id)

    visited_count = sum(
        1
        for row in rows
        if row["status"] != "none"
    )

    total = len(PREFECTURES)

    percent = 0

    if total > 0:
        percent = int(
            (visited_count / total) * 100
        )

    status_counts = {
        status: 0
        for status in STATUS_OPTIONS
    }

    for row in rows:
        status = row["status"]

        if status not in status_counts:
            status = "none"

        status_counts[status] += 1

    return {
        "visited": visited_count,
        "total": total,
        "percent": percent,
        "status_counts": status_counts
    }


def status_data(status):
    """
    状態に対応する表示情報を返します。
    """
    return STATUS_OPTIONS.get(
        status,
        STATUS_OPTIONS["none"]
    )


def clear_prefecture_cache(user_id=None):
    """
    地図キャッシュを削除します。
    通常はupdate_prefectureから自動で呼ばれるため、
    直接使う必要はありません。
    """
    if user_id:
        _prefecture_cache.pop(
            user_id,
            None
        )
        return

    _prefecture_cache.clear()