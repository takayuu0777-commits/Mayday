from datetime import datetime, date
from collections import defaultdict
import calendar as cal

from modules.database import connect


CATEGORY_ICONS = {
    "学習": "📚",
    "仕事": "💼",
    "メディア": "🎬",
    "健康": "💪",
    "買い物": "🛒",
    "その他": "✦"
}


def get_icon(category):
    return CATEGORY_ICONS.get(category or "その他", "✦")


def fetch_data():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM logs
    ORDER BY created_at DESC
    """)

    rows = c.fetchall()
    conn.close()

    data = defaultdict(list)

    for row in rows:
        date_key = row["date_key"] or row["created_at"][:10]
        data[date_key].append(row)

    return dict(data)


def fetch_memos():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM calendar_memos
    ORDER BY date_key DESC, created_at DESC
    """)

    rows = c.fetchall()
    conn.close()

    data = defaultdict(list)

    for row in rows:
        data[row["date_key"]].append(row)

    return dict(data)


def add_calendar_memo(date_key, text, icon="📝"):
    date_key = (date_key or "").strip()
    text = (text or "").strip()
    icon = (icon or "📝").strip()

    if not date_key or not text:
        return

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO calendar_memos
    (date_key, text, icon, created_at)
    VALUES (?, ?, ?, ?)
    """, (
        date_key,
        text,
        icon,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def calendar_icons():
    logs = fetch_data()
    memos = fetch_memos()
    result = {}

    for date_key, items in logs.items():
        icons = []

        for log in items:
            icons.append(get_icon(log["category"]))

        result[date_key] = icons[:4]

    for date_key, items in memos.items():
        if date_key not in result:
            result[date_key] = []

        for memo in items:
            result[date_key].append(memo["icon"])

        result[date_key] = result[date_key][:4]

    return result


def month_calendar(year=None, month=None):
    today = date.today()

    year = int(year or today.year)
    month = int(month or today.month)

    month_days = cal.Calendar(firstweekday=0).monthdatescalendar(year, month)
    icons = calendar_icons()

    weeks = []

    for week in month_days:
        week_items = []

        for day in week:
            date_key = day.strftime("%Y-%m-%d")

            week_items.append({
                "date": day,
                "date_key": date_key,
                "day": day.day,
                "is_current_month": day.month == month,
                "is_today": day == today,
                "icons": icons.get(date_key, [])
            })

        weeks.append(week_items)

    prev_month = month - 1
    prev_year = year

    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year

    if next_month == 13:
        next_month = 1
        next_year += 1

    return {
        "year": year,
        "month": month,
        "weeks": weeks,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month
    }


def day_detail(date_key):
    logs = fetch_data().get(date_key, [])
    memos = fetch_memos().get(date_key, [])

    return {
        "date_key": date_key,
        "logs": logs,
        "memos": memos
    }


def fetch_life_events():
    return []


def add_life_event(title, event_date, description):
    return