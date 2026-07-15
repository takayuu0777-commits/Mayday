from datetime import date, datetime
from urllib.parse import urlparse
import os

from flask import (
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from modules.database import (
    init,
    connect,
    is_postgres
)

from modules.auth import (
    authenticate_user,
    create_user,
    get_user
)

from modules.logs import save

from modules.search import search_logs

from modules.library import (
    fetch_grouped,
    fetch_item,
    fetch_review,
    add_item,
    update_item,
    delete_item,
    add_review,
    GENRES
)

from modules.calendar import (
    month_calendar,
    day_detail,
    add_calendar_memo,
    delete_calendar_memo
)

from modules.stats import life_stats

from modules.tips import today_tip

from modules.themes import (
    load_themes,
    is_owned,
    owned_themes
)

from modules.achievements import (
    all_achievements,
    compact_categories,
    achievements_by_group,
    find_achievement
)

from modules.profile import (
    get_profile,
    ensure_profile,
    load_titles,
    load_icons,
    load_backgrounds,
    update_profile
)

from modules.shopping import (
    fetch_items as fetch_shopping,
    add_item as add_shopping,
    complete_item as complete_shopping,
    guess_icon
)

from modules.goals import (
    fetch_goals,
    fetch_home_goals,
    add_goal,
    complete_goal,
    GOAL_TYPES
)

from modules.life_settings import (
    load_categories,
    update_categories
)

from modules.todo import (
    fetch_todos,
    add_todo,
    complete_todo,
    priority_icon,
    priority_label,
    days_left
)

from modules.weather import (
    weather_summary,
    hourly_forecast,
    weekly_forecast
)

from modules.statistics import fetch_statistics

from modules.japan_map import (
    fetch_prefectures,
    update_prefecture,
    japan_progress,
    status_data,
    STATUS_OPTIONS
)


# ==========================
# Flask基本設定
# ==========================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "second-brain-local-development-key"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=bool(
        os.environ.get("RENDER")
    ),
    PERMANENT_SESSION_LIFETIME=(
        60 * 60 * 24 * 30
    )
)


PUBLIC_ENDPOINTS = {
    "login",
    "register",
    "static"
}


# ==========================
# 共通処理
# ==========================

def current_user_id():
    current_user = getattr(
        g,
        "current_user",
        None
    )

    if not current_user:
        return None

    return current_user["id"]


def safe_next_url(target):
    if not target:
        return None

    parsed = urlparse(target)

    if parsed.scheme or parsed.netloc:
        return None

    if not target.startswith("/"):
        return None

    return target


def ensure_login_bonus_tables():
    conn = connect()

    try:
        c = conn.cursor()

        if is_postgres():
            c.execute("""
            CREATE TABLE IF NOT EXISTS user_login_days (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                date_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (user_id, date_key)
            )
            """)

        else:
            c.execute("""
            CREATE TABLE IF NOT EXISTS user_login_days (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (user_id, date_key)
            )
            """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def give_login_bonus(user_id):
    if not user_id:
        return False

    ensure_profile(user_id)
    ensure_login_bonus_tables()

    today_key = date.today().strftime(
        "%Y-%m-%d"
    )

    now = datetime.now().isoformat()

    conn = connect()

    try:
        c = conn.cursor()

        if is_postgres():
            c.execute("""
            INSERT INTO user_login_days
            (
                user_id,
                date_key,
                created_at
            )
            VALUES (?, ?, ?)
            ON CONFLICT (
                user_id,
                date_key
            )
            DO NOTHING
            """, (
                user_id,
                today_key,
                now
            ))

        else:
            c.execute("""
            INSERT OR IGNORE INTO user_login_days
            (
                user_id,
                date_key,
                created_at
            )
            VALUES (?, ?, ?)
            """, (
                user_id,
                today_key,
                now
            ))

        received_bonus = (
            c.rowcount == 1
        )

        if received_bonus:
            c.execute("""
            UPDATE user_profiles
            SET coins = coins + 1
            WHERE user_id = ?
            """, (user_id,))

        conn.commit()

        return received_bonus

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


@app.before_request
def before_request():
    if "theme" not in session:
        session["theme"] = "gold"

    if not is_owned(
        session.get("theme", "gold")
    ):
        session["theme"] = "gold"

    user_id = session.get("user_id")

    g.current_user = (
        get_user(user_id)
        if user_id
        else None
    )

    if user_id and not g.current_user:
        session.clear()
        session["theme"] = "gold"

    if request.endpoint in PUBLIC_ENDPOINTS:
        return None

    if request.endpoint is None:
        return None

    if not g.current_user:
        next_url = request.full_path

        if next_url.endswith("?"):
            next_url = next_url[:-1]

        return redirect(
            url_for(
                "login",
                next=next_url
            )
        )

    logged_in_user_id = g.current_user["id"]

    if (
        session.get("login_bonus_user_id")
        != logged_in_user_id
    ):
        give_login_bonus(
            logged_in_user_id
        )

        session["login_bonus_user_id"] = (
            logged_in_user_id
        )

    return None


@app.context_processor
def inject_global_data():
    return {
        "current_user": getattr(
            g,
            "current_user",
            None
        ),
        "theme": session.get(
            "theme",
            "gold"
        )
    }


# ==========================
# 認証
# ==========================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():
    if g.current_user:
        return redirect("/")

    error = None
    entered_name = ""
    entered_email = ""

    if request.method == "POST":
        entered_name = request.form.get(
            "name",
            ""
        ).strip()

        entered_email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        password_confirm = request.form.get(
            "password_confirm",
            ""
        )

        if password != password_confirm:
            error = (
                "確認用パスワードが"
                "一致しません。"
            )

        else:
            result = create_user(
                entered_name,
                entered_email,
                password
            )

            if result["success"]:
                session.clear()

                session["user_id"] = (
                    result["user_id"]
                )

                session["theme"] = "gold"
                session.permanent = True

                return redirect("/")

            error = result["message"]

    return render_template(
        "register.html",
        error=error,
        name=entered_name,
        email=entered_email,
        theme=session.get(
            "theme",
            "gold"
        )
    )


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():
    if g.current_user:
        return redirect("/")

    error = None
    entered_email = ""

    if request.method == "POST":
        entered_email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        result = authenticate_user(
            entered_email,
            password
        )

        if result["success"]:
            next_url = safe_next_url(
                request.args.get("next")
            )

            session.clear()

            session["user_id"] = (
                result["user"]["id"]
            )

            session["theme"] = "gold"
            session.permanent = True

            return redirect(
                next_url or "/"
            )

        error = result["message"]

    return render_template(
        "login.html",
        error=error,
        email=entered_email,
        theme=session.get(
            "theme",
            "gold"
        )
    )


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/login")


# ==========================
# ホーム
# ==========================

@app.route("/")
def home():
    user_id = current_user_id()

    return render_template(
        "home.html",
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        shopping=fetch_shopping(
            user_id
        )[:3],
        todos=fetch_todos(
            user_id,
            3
        ),
        weather=weather_summary(),
        goals=fetch_home_goals(
            user_id
        ),
        guess_icon=guess_icon,
        priority_icon=priority_icon,
        priority_label=priority_label,
        days_left=days_left,
        today_tip=today_tip(),
        theme=session["theme"]
    )


@app.route(
    "/add",
    methods=["POST"]
)
def add():
    text = request.form.get(
        "text",
        ""
    ).strip()

    if text:
        save(
            current_user_id(),
            text
        )

    return redirect("/")


# ==========================
# 検索
# ==========================

@app.route("/search")
def search():
    user_id = current_user_id()

    return render_template(
        "search.html",
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        theme=session["theme"]
    )


@app.route("/api/search")
def api_search():
    query = request.args.get(
        "q",
        ""
    )

    rows = search_logs(
        current_user_id(),
        query
    )

    return jsonify([
        dict(row)
        for row in rows
    ])


# ==========================
# Library
# ==========================

@app.route("/library")
def library():
    user_id = current_user_id()

    return render_template(
        "library.html",
        data=fetch_grouped(user_id),
        genres=GENRES,
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        theme=session["theme"]
    )


@app.route(
    "/library/add",
    methods=["POST"]
)
def library_add():
    user_id = current_user_id()

    item_id = add_item(
        user_id,
        request.form.get("title"),
        request.form.get("genre"),
        request.form.get(
            "rating",
            0
        ),
        request.form.get(
            "review",
            ""
        )
    )

    if item_id:
        return redirect(
            f"/library/item/{item_id}"
        )

    return redirect("/library")


@app.route(
    "/library/item/<item_id>"
)
def library_detail(item_id):
    user_id = current_user_id()

    return render_template(
        "library-detail.html",
        item=fetch_item(
            user_id,
            item_id
        ),
        review=fetch_review(
            user_id,
            item_id
        ),
        genres=GENRES,
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        theme=session["theme"]
    )


@app.route(
    "/library/item/<item_id>/update",
    methods=["POST"]
)
def library_update(item_id):
    update_item(
        current_user_id(),
        item_id,
        request.form.get("title"),
        request.form.get("genre"),
        request.form.get(
            "rating",
            0
        ),
        request.form.get(
            "review",
            ""
        )
    )

    return redirect(
        f"/library/item/{item_id}"
    )


@app.route(
    "/library/item/<item_id>/delete",
    methods=["POST"]
)
def library_delete(item_id):
    delete_item(
        current_user_id(),
        item_id
    )

    return redirect("/library")


@app.route(
    "/library/item/<item_id>/review",
    methods=["POST"]
)
def library_review(item_id):
    add_review(
        current_user_id(),
        item_id,
        request.form.get("text"),
        request.form.get("rating")
    )

    return redirect(
        f"/library/item/{item_id}"
    )


# ==========================
# カレンダー
# ==========================

@app.route("/calendar")
def calendar():
    user_id = current_user_id()

    year = request.args.get("year")
    month = request.args.get("month")
    selected = request.args.get("date")

    if not selected:
        selected = date.today().strftime(
            "%Y-%m-%d"
        )

    calendar_data = month_calendar(
        user_id,
        year,
        month
    )

    return render_template(
        "calendar.html",
        calendar_data=calendar_data,
        selected_day=day_detail(
            user_id,
            selected
        ),
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        theme=session["theme"]
    )


@app.route(
    "/calendar/memo/add",
    methods=["POST"]
)
def calendar_memo_add():
    user_id = current_user_id()

    date_key = request.form.get(
        "date_key"
    )

    add_calendar_memo(
        user_id,
        date_key,
        request.form.get("text"),
        request.form.get(
            "icon",
            "📝"
        )
    )

    year = request.form.get("year")
    month = request.form.get("month")

    return redirect(
        f"/calendar?year={year}"
        f"&month={month}"
        f"&date={date_key}"
    )


@app.route(
    "/calendar/memo/<memo_id>/delete",
    methods=["POST"]
)
def calendar_memo_delete(memo_id):
    user_id = current_user_id()

    delete_calendar_memo(
        user_id,
        memo_id
    )

    date_key = request.form.get(
        "date_key",
        date.today().strftime(
            "%Y-%m-%d"
        )
    )

    return redirect(
        f"/calendar?date={date_key}"
    )


# ==========================
# ToDo
# ==========================

@app.route(
    "/todo/add",
    methods=["POST"]
)
def todo_add():
    add_todo(
        current_user_id(),
        request.form.get("title"),
        request.form.get(
            "priority",
            "middle"
        ),
        request.form.get(
            "deadline",
            ""
        )
    )

    return redirect("/")


@app.route(
    "/todo/done/<todo_id>",
    methods=["POST"]
)
def todo_done(todo_id):
    complete_todo(
        current_user_id(),
        todo_id
    )

    return redirect("/")


# ==========================
# 実績
# ==========================

@app.route("/achievements")
def achievements():
    user_id = current_user_id()

    return render_template(
        "achievements.html",
        achievements=all_achievements(
            user_id
        ),
        categories=compact_categories(
            user_id
        ),
        selected_group=request.args.get(
            "group",
            "all"
        ),
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        theme=session["theme"]
    )


@app.route(
    "/achievements/group/<group_name>"
)
def achievement_group(group_name):
    user_id = current_user_id()

    return render_template(
        "achievements.html",
        achievements=(
            achievements_by_group(
                user_id,
                group_name
            )
        ),
        categories=compact_categories(
            user_id
        ),
        selected_group=group_name,
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        theme=session["theme"]
    )


@app.route(
    "/achievements/<achievement_id>"
)
def achievement_detail(
    achievement_id
):
    user_id = current_user_id()

    return render_template(
        "achievement-detail.html",
        achievement=find_achievement(
            user_id,
            achievement_id
        ),
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        theme=session["theme"]
    )


# ==========================
# プロフィール
# ==========================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():
    user_id = current_user_id()

    if request.method == "POST":
        update_profile(
            user_id,
            request.form.get("title"),
            request.form.get("icon"),
            request.form.get(
                "background"
            ),
            request.form.get("bio")
        )

        return redirect("/profile")

    return render_template(
        "profile.html",
        profile=get_profile(user_id),
        titles=load_titles(),
        icons=load_icons(),
        backgrounds=load_backgrounds(),
        stats=life_stats(user_id),
        theme=session["theme"]
    )


@app.route("/stats")
def stats():
    user_id = current_user_id()

    return render_template(
        "stats.html",
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        theme=session["theme"]
    )


# ==========================
# Statistics
# ==========================

@app.route("/statistics")
def statistics():
    user_id = current_user_id()

    statistics_data = (
        fetch_statistics(user_id)
    )

    prefectures = fetch_prefectures(
        user_id
    )

    progress = japan_progress(
        user_id,
        prefectures
    )

    return render_template(
        "statistics.html",
        basic_stats=statistics_data[
            "basic_stats"
        ],
        library_stats=statistics_data[
            "library_stats"
        ],
        todo_stats=statistics_data[
            "todo_stats"
        ],
        category_stats=statistics_data[
            "category_stats"
        ],
        japan_progress=progress,
        stats=life_stats(user_id),
        profile=get_profile(user_id),
        theme=session["theme"]
    )


# ==========================
# 日本地図
# ==========================

@app.route("/japan-map")
def japan_map():
    user_id = current_user_id()

    prefectures = fetch_prefectures(
        user_id
    )

    progress = japan_progress(
        user_id,
        prefectures
    )

    return render_template(
        "japan-map.html",
        prefectures=prefectures,
        japan_progress=progress,
        status_options=STATUS_OPTIONS,
        status_data=status_data,
        profile=get_profile(user_id),
        stats=life_stats(user_id),
        theme=session["theme"]
    )


@app.route(
    "/statistics/prefecture/update",
    methods=["POST"]
)
def prefecture_update():
    update_prefecture(
        current_user_id(),
        request.form.get("name"),
        request.form.get("status")
    )

    return redirect("/japan-map")


# ==========================
# ショップ・設定
# ==========================

@app.route("/shop")
def shop():
    user_id = current_user_id()

    return render_template(
        "shop.html",
        themes=load_themes(),
        owned=owned_themes(),
        profile=get_profile(user_id),
        stats=life_stats(user_id),
        theme=session["theme"]
    )


@app.route(
    "/settings",
    methods=["GET", "POST"]
)
def settings():
    user_id = current_user_id()

    if request.method == "POST":
        selected_theme = request.form.get(
            "theme"
        )

        if (
            selected_theme
            and is_owned(selected_theme)
        ):
            session["theme"] = selected_theme

        update_categories(
            user_id,
            request.form
        )

        return redirect("/settings")

    return render_template(
        "settings.html",
        themes=load_themes(),
        owned=owned_themes(),
        current_theme=session["theme"],
        categories=load_categories(
            user_id
        ),
        profile=get_profile(user_id),
        stats=life_stats(user_id),
        theme=session["theme"]
    )


# ==========================
# 目標
# ==========================

@app.route("/goals")
def goals():
    user_id = current_user_id()

    return render_template(
        "goals.html",
        goals=fetch_goals(user_id),
        goal_types=GOAL_TYPES,
        profile=get_profile(user_id),
        stats=life_stats(user_id),
        theme=session["theme"]
    )


@app.route(
    "/goals/add",
    methods=["POST"]
)
def goals_add():
    add_goal(
        current_user_id(),
        request.form.get("title"),
        request.form.get(
            "goal_type"
        )
    )

    return redirect("/goals")


@app.route(
    "/goals/done/<goal_id>",
    methods=["POST"]
)
def goals_done(goal_id):
    complete_goal(
        current_user_id(),
        goal_id
    )

    return redirect("/goals")


# ==========================
# 買い物
# ==========================

@app.route("/shopping")
def shopping():
    user_id = current_user_id()

    return render_template(
        "shopping.html",
        items=fetch_shopping(user_id),
        guess_icon=guess_icon,
        profile=get_profile(user_id),
        stats=life_stats(user_id),
        theme=session["theme"]
    )


@app.route(
    "/shopping/add",
    methods=["POST"]
)
def shopping_add():
    add_shopping(
        current_user_id(),
        request.form.get("name")
    )

    return redirect("/shopping")


@app.route(
    "/shopping/done/<item_id>",
    methods=["POST"]
)
def shopping_done(item_id):
    complete_shopping(
        current_user_id(),
        item_id
    )

    return redirect("/shopping")


# ==========================
# 天気
# ==========================

@app.route("/weather")
def weather():
    user_id = current_user_id()

    return render_template(
        "weather_detail.html",
        weather=weather_summary(),
        hourly=hourly_forecast(),
        weekly=weekly_forecast(),
        profile=get_profile(user_id),
        stats=life_stats(user_id),
        theme=session["theme"]
    )


# ==========================
# 起動
# ==========================

init()


if __name__ == "__main__":
    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=not bool(
            os.environ.get("RENDER")
        )
    )