from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime, date

from modules.database import init, connect
from modules.logs import save
from modules.search import search_logs
from modules.library import (
    fetch_grouped,
    fetch_item,
    fetch_reviews,
    add_item,
    update_item,
    delete_item,
    add_review,
    GENRES
)
from modules.calendar import (
    fetch_data,
    calendar_icons,
    month_calendar,
    day_detail,
    add_calendar_memo
)
from modules.stats import life_stats
from modules.tips import today_tip
from modules.themes import load_themes, is_owned, owned_themes
from modules.achievements import all_achievements, compact_categories, achievements_by_group, find_achievement
from modules.profile import get_profile, load_titles, load_icons, load_backgrounds, update_profile
from modules.shopping import fetch_items as fetch_shopping, add_item as add_shopping, complete_item as complete_shopping, guess_icon
from modules.goals import fetch_goals, fetch_home_goals, add_goal, complete_goal, GOAL_TYPES
from modules.life_settings import load_categories, update_categories, enabled_categories

from modules.todo import (
    fetch_todos,
    add_todo,
    complete_todo,
    priority_icon,
    days_left
)
from modules.weather import weather_summary, hourly_forecast, weekly_forecast
from modules.statistics import basic_statistics, library_statistics, todo_statistics
from modules.japan_map import (
    fetch_prefectures,
    update_prefecture,
    japan_progress,
    status_data,
    STATUS_OPTIONS
)


app = Flask(__name__)
app.secret_key = "brain-os"


def load_json(file_name):
    path = os.path.join(os.getcwd(), "data", file_name)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def give_login_bonus():
    today = date.today().strftime("%Y-%m-%d")

    conn = connect()
    c = conn.cursor()

    c.execute("SELECT date_key FROM login_days WHERE date_key = ?", (today,))
    exists = c.fetchone()

    if not exists:
        c.execute("""
        INSERT INTO login_days
        (date_key, created_at)
        VALUES (?, ?)
        """, (today, datetime.now().isoformat()))

        c.execute("""
        UPDATE profile
        SET coins = coins + 1
        WHERE id = 1
        """)

    conn.commit()
    conn.close()


@app.before_request
def before():
    init()

    if "theme" not in session:
        session["theme"] = "gold"

    if not is_owned(session["theme"]):
        session["theme"] = "gold"

    give_login_bonus()


@app.route("/")
def home():
    return render_template(
        "home.html",
        stats=life_stats(),
        profile=get_profile(),
        shopping=fetch_shopping()[:3],
        todos=fetch_todos(3),
        weather=weather_summary(),
        goals=fetch_home_goals(),
        guess_icon=guess_icon,
        priority_icon=priority_icon,
        days_left=days_left,
        today_tip=today_tip(),
        theme=session["theme"]
    )


@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("text")

    if text:
        save(text)

    return redirect("/")


@app.route("/search")
def search():
    return render_template(
        "search.html",
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "")
    return jsonify(search_logs(q))


@app.route("/library")
def library():
    return render_template(
        "library.html",
        data=fetch_grouped(),
        genres=GENRES,
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/library/add", methods=["POST"])
def library_add():
    title = request.form.get("title")
    genre = request.form.get("genre")
    rating = request.form.get("rating", 0)
    review = request.form.get("review", "")

    item_id = add_item(title, genre, rating, review)

    if item_id:
        return redirect(f"/library/item/{item_id}")

    return redirect("/library")


@app.route("/library/item/<item_id>")
def library_detail(item_id):
    return render_template(
        "library-detail.html",
        item=fetch_item(item_id),
        reviews=fetch_reviews(item_id),
        genres=GENRES,
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/library/item/<item_id>/update", methods=["POST"])
def library_update(item_id):
    update_item(
        item_id,
        request.form.get("title"),
        request.form.get("genre"),
        request.form.get("rating", 0)
    )

    return redirect(f"/library/item/{item_id}")


@app.route("/library/item/<item_id>/delete", methods=["POST"])
def library_delete(item_id):
    delete_item(item_id)
    return redirect("/library")


@app.route("/library/item/<item_id>/review", methods=["POST"])
def library_review(item_id):
    add_review(
        item_id,
        request.form.get("text"),
        request.form.get("rating")
    )

    return redirect(f"/library/item/{item_id}")


@app.route("/calendar")
def calendar():
    year = request.args.get("year")
    month = request.args.get("month")
    selected = request.args.get("date")

    cal_data = month_calendar(year, month)

    if not selected:
        selected = date.today().strftime("%Y-%m-%d")

    return render_template(
        "calendar.html",
        calendar_data=cal_data,
        selected_day=day_detail(selected),
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/calendar/memo/add", methods=["POST"])
def calendar_memo_add():
    add_calendar_memo(
        request.form.get("date_key"),
        request.form.get("text"),
        request.form.get("icon", "📝")
    )

    year = request.form.get("year")
    month = request.form.get("month")
    date_key = request.form.get("date_key")

    return redirect(f"/calendar?year={year}&month={month}&date={date_key}")


@app.route("/achievements")
def achievements():
    return render_template(
        "achievements.html",
        achievements=all_achievements(),
        categories=compact_categories(),
        selected_group=request.args.get("group", "all"),
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/achievements/group/<group>")
def achievement_group(group):
    return render_template(
        "achievements.html",
        achievements=achievements_by_group(group),
        categories=compact_categories(),
        selected_group=group,
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/achievements/<achievement_id>")
def achievement_detail(achievement_id):
    return render_template(
        "achievement-detail.html",
        achievement=find_achievement(achievement_id),
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        update_profile(
            request.form.get("title"),
            request.form.get("icon"),
            request.form.get("background"),
            request.form.get("bio")
        )

        return redirect("/profile")

    return render_template(
        "profile.html",
        profile=get_profile(),
        titles=load_titles(),
        icons=load_icons(),
        backgrounds=load_backgrounds(),
        stats=life_stats(),
        theme=session["theme"]
    )


@app.route("/stats")
def stats():
    return render_template(
        "stats.html",
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/statistics")
def statistics():
    return render_template(
        "statistics.html",
        basic_stats=basic_statistics(),
        library_stats=library_statistics(),
        todo_stats=todo_statistics(),
        prefectures=fetch_prefectures(),
        japan_progress=japan_progress(),
        status_options=STATUS_OPTIONS,
        status_data=status_data,
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/statistics/prefecture/update", methods=["POST"])
def prefecture_update():
    update_prefecture(
        request.form.get("name"),
        request.form.get("status")
    )

    return redirect("/statistics")


@app.route("/shop")
def shop():
    return render_template(
        "shop.html",
        themes=load_themes(),
        owned=owned_themes(),
        profile=get_profile(),
        stats=life_stats(),
        theme=session["theme"]
    )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        selected_theme = request.form.get("theme")

        if selected_theme:
            session["theme"] = selected_theme

        update_categories(request.form)

        return redirect("/settings")

    return render_template(
        "settings.html",
        themes=load_themes(),
        owned=owned_themes(),
        current_theme=session["theme"],
        categories=load_categories(),
        profile=get_profile(),
        stats=life_stats(),
        theme=session["theme"]
    )


@app.route("/goals")
def goals():
    return render_template(
        "goals.html",
        goals=fetch_goals(),
        goal_types=GOAL_TYPES,
        profile=get_profile(),
        stats=life_stats(),
        theme=session["theme"]
    )


@app.route("/goals/add", methods=["POST"])
def goals_add():
    add_goal(
        request.form.get("title"),
        request.form.get("goal_type")
    )

    return redirect("/goals")


@app.route("/goals/done/<goal_id>", methods=["POST"])
def goals_done(goal_id):
    complete_goal(goal_id)
    return redirect("/goals")


@app.route("/shopping")
def shopping():
    return render_template(
        "shopping.html",
        items=fetch_shopping(),
        guess_icon=guess_icon,
        profile=get_profile(),
        stats=life_stats(),
        theme=session["theme"]
    )