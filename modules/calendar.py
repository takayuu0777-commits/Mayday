from collections import defaultdict
from datetime import date, datetime, timedelta
import calendar as cal

from modules.database import connect


CATEGORY_ICONS = {
    "学習": "📚",
    "仕事": "💼",
    "メディア": "🎬",
    "思考": "💡",
    "人": "👥",
    "場所": "📍",
    "健康": "💪",
    "買い物": "🛒",
    "目標": "🎯",
    "実績": "🏆",
    "その他": "✦"
}


MEMO_ICONS = [
    {"value": "📝", "label": "メモ"},
    {"value": "📚", "label": "学習"},
    {"value": "🎬", "label": "メディア"},
    {"value": "🚴", "label": "運動"},
    {"value": "✈️", "label": "旅行"},
    {"value": "🏆", "label": "達成"},
    {"value": "💼", "label": "仕事"},
    {"value": "💡", "label": "発見"},
    {"value": "🍽️", "label": "食事"},
    {"value": "👥", "label": "人"},
    {"value": "📍", "label": "場所"}
]


def get_icon(category):
    return CATEGORY_ICONS.get(
        category or "その他",
        CATEGORY_ICONS["その他"]
    )


def normalize_year_month(
    year=None,
    month=None
):
    today = date.today()

    try:
        selected_year = int(
            year or today.year
        )
    except (TypeError, ValueError):
        selected_year = today.year

    try:
        selected_month = int(
            month or today.month
        )
    except (TypeError, ValueError):
        selected_month = today.month

    if selected_month < 1 or selected_month > 12:
        selected_month = today.month

    if selected_year < 1900 or selected_year > 2200:
        selected_year = today.year

    return selected_year, selected_month


def month_range(year, month):
    start_date = date(
        year,
        month,
        1
    )

    if month == 12:
        next_month = date(
            year + 1,
            1,
            1
        )
    else:
        next_month = date(
            year,
            month + 1,
            1
        )

    end_date = (
        next_month -
        timedelta(days=1)
    )

    return (
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )


def fetch_data(
    user_id,
    start_date=None,
    end_date=None
):
    if not user_id:
        return {}

    conn = connect()
    c = conn.cursor()

    if start_date and end_date:
        c.execute("""
        SELECT
            id,
            text,
            category,
            summary,
            created_at,
            date_key
        FROM logs
        WHERE user_id = ?
          AND date_key >= ?
          AND date_key <= ?
        ORDER BY created_at DESC
        """, (
            user_id,
            start_date,
            end_date
        ))

    else:
        c.execute("""
        SELECT
            id,
            text,
            category,
            summary,
            created_at,
            date_key
        FROM logs
        WHERE user_id = ?
        ORDER BY created_at DESC
        """, (user_id,))

    rows = c.fetchall()
    conn.close()

    data = defaultdict(list)

    for row in rows:
        created_at = (
            row["created_at"] or ""
        )

        date_key = row["date_key"]

        if (
            not date_key
            and len(created_at) >= 10
        ):
            date_key = created_at[:10]

        if date_key:
            data[date_key].append(row)

    return dict(data)


def fetch_memos(
    user_id,
    start_date=None,
    end_date=None
):
    if not user_id:
        return {}

    conn = connect()
    c = conn.cursor()

    if start_date and end_date:
        c.execute("""
        SELECT
            id,
            date_key,
            text,
            icon,
            created_at
        FROM calendar_memos
        WHERE user_id = ?
          AND date_key >= ?
          AND date_key <= ?
        ORDER BY
            date_key DESC,
            created_at DESC
        """, (
            user_id,
            start_date,
            end_date
        ))

    else:
        c.execute("""
        SELECT
            id,
            date_key,
            text,
            icon,
            created_at
        FROM calendar_memos
        WHERE user_id = ?
        ORDER BY
            date_key DESC,
            created_at DESC
        """, (user_id,))

    rows = c.fetchall()
    conn.close()

    data = defaultdict(list)

    for row in rows:
        date_key = row["date_key"]

        if date_key:
            data[date_key].append(row)

    return dict(data)


def add_calendar_memo(
    user_id,
    date_key,
    text,
    icon="📝"
):
    clean_date_key = (
        date_key or ""
    ).strip()

    clean_text = (
        text or ""
    ).strip()

    clean_icon = (
        icon or "📝"
    ).strip()

    if (
        not user_id
        or not clean_date_key
        or not clean_text
    ):
        return False

    try:
        datetime.strptime(
            clean_date_key,
            "%Y-%m-%d"
        )
    except ValueError:
        return False

    allowed_icons = {
        item["value"]
        for item in MEMO_ICONS
    }

    if clean_icon not in allowed_icons:
        clean_icon = "📝"

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO calendar_memos
    (
        user_id,
        date_key,
        text,
        icon,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        clean_date_key,
        clean_text,
        clean_icon,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return True


def delete_calendar_memo(
    user_id,
    memo_id
):
    if not user_id or not memo_id:
        return False

    conn = connect()
    c = conn.cursor()

    c.execute("""
    DELETE FROM calendar_memos
    WHERE id = ?
      AND user_id = ?
    """, (
        memo_id,
        user_id
    ))

    deleted = c.rowcount == 1

    conn.commit()
    conn.close()

    return deleted


def build_calendar_icons(
    logs,
    memos
):
    result = {}

    all_dates = (
        set(logs.keys())
        |
        set(memos.keys())
    )

    for date_key in all_dates:
        icons = []

        for log in logs.get(
            date_key,
            []
        ):
            icon = get_icon(
                log["category"]
            )

            if icon not in icons:
                icons.append(icon)

        for memo in memos.get(
            date_key,
            []
        ):
            icon = (
                memo["icon"] or "📝"
            )

            if icon not in icons:
                icons.append(icon)

        result[date_key] = icons[:4]

    return result


def calendar_icons(
    user_id,
    year=None,
    month=None
):
    selected_year, selected_month = (
        normalize_year_month(
            year,
            month
        )
    )

    start_date, end_date = month_range(
        selected_year,
        selected_month
    )

    logs = fetch_data(
        user_id,
        start_date,
        end_date
    )

    memos = fetch_memos(
        user_id,
        start_date,
        end_date
    )

    return build_calendar_icons(
        logs,
        memos
    )


def month_calendar(
    user_id,
    year=None,
    month=None
):
    today = date.today()

    selected_year, selected_month = (
        normalize_year_month(
            year,
            month
        )
    )

    start_date, end_date = month_range(
        selected_year,
        selected_month
    )

    logs = fetch_data(
        user_id,
        start_date,
        end_date
    )

    memos = fetch_memos(
        user_id,
        start_date,
        end_date
    )

    icons = build_calendar_icons(
        logs,
        memos
    )

    calendar_builder = cal.Calendar(
        firstweekday=0
    )

    month_days = (
        calendar_builder
        .monthdatescalendar(
            selected_year,
            selected_month
        )
    )

    weeks = []

    for week in month_days:
        week_items = []

        for day in week:
            date_key = day.strftime(
                "%Y-%m-%d"
            )

            week_items.append({
                "date": day,
                "date_key": date_key,
                "day": day.day,
                "is_current_month": (
                    day.month ==
                    selected_month
                ),
                "is_today": (
                    day == today
                ),
                "icons": icons.get(
                    date_key,
                    []
                )
            })

        weeks.append(week_items)

    if selected_month == 1:
        prev_year = (
            selected_year - 1
        )
        prev_month = 12
    else:
        prev_year = selected_year
        prev_month = (
            selected_month - 1
        )

    if selected_month == 12:
        next_year = (
            selected_year + 1
        )
        next_month = 1
    else:
        next_year = selected_year
        next_month = (
            selected_month + 1
        )

    return {
        "year": selected_year,
        "month": selected_month,
        "weeks": weeks,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
        "today_key": today.strftime(
            "%Y-%m-%d"
        )
    }


def day_detail(
    user_id,
    date_key
):
    clean_date_key = (
        date_key
        or date.today().strftime(
            "%Y-%m-%d"
        )
    ).strip()

    try:
        selected_date = datetime.strptime(
            clean_date_key,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        selected_date = date.today()

        clean_date_key = (
            selected_date.strftime(
                "%Y-%m-%d"
            )
        )

    logs = fetch_data(
        user_id,
        clean_date_key,
        clean_date_key
    ).get(
        clean_date_key,
        []
    )

    memos = fetch_memos(
        user_id,
        clean_date_key,
        clean_date_key
    ).get(
        clean_date_key,
        []
    )

    weekday_names = [
        "月曜日",
        "火曜日",
        "水曜日",
        "木曜日",
        "金曜日",
        "土曜日",
        "日曜日"
    ]

    return {
        "date_key": clean_date_key,
        "year": selected_date.year,
        "month": selected_date.month,
        "day": selected_date.day,
        "weekday": weekday_names[
            selected_date.weekday()
        ],
        "display_date": (
            f"{selected_date.year}年"
            f"{selected_date.month}月"
            f"{selected_date.day}日"
        ),
        "is_today": (
            selected_date ==
            date.today()
        ),
        "logs": logs,
        "memos": memos,
        "item_count": (
            len(logs) +
            len(memos)
        )
    }


def fetch_life_events(user_id):
    return []


def add_life_event(
    user_id,
    title,
    event_date,
    description
):
    return False