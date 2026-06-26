from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
import uuid
from datetime import datetime, date

from modules.database import init, connect
from modules.logs import save
from modules.search import search_logs
from modules.library import (
    fetch_grouped, fetch_by_genre, fetch_item, fetch_reviews,
    add_item, update_item, delete_item, add_review, GENRES
)
from modules.calendar import fetch_data, fetch_life_events, add_life_event
from modules.stats import life_stats
from modules.tips import today_tip
from modules.themes import load_themes, owned_themes, buy_theme, is_owned
from modules.achievements import (
    achievement_categories,
    achievements_by_category,
    find_achievement
)

from modules.profile import (
    get_profile,
    load_titles,
    load_icons,
    update_profile
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
        session["theme"] = "dream"

    if not is_owned(session["theme"]):
        session["theme"] = "dream"

    give_login_bonus()


@app.route("/")
def home():
    return render_template(
        "home.html",
        stats=life_stats(),
        profile=get_profile(),
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
    return render_template("search.html", theme=session["theme"])


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
        theme=session["theme"]
    )


@app.route("/library/add", methods=["POST"])
def library_add():
    title = request.form.get("title")
    genre = request.form.get("genre")
    rating = request.form.get("rating", 0)
    review = request.form.get("review")

    item_id = add_item(title, genre, rating)

    if item_id and review:
        add_review(item_id, review, rating)

    if item_id:
        return redirect(f"/library/item/{item_id}")

    return redirect("/library")


@app.route("/library/genre/<genre>")
def library_genre(genre):
    return render_template(
        "library.html",
        data={genre: fetch_by_genre(genre)},
        genres=GENRES,
        selected_genre=genre,
        theme=session["theme"]
    )


@app.route("/library/item/<item_id>")
def library_detail(item_id):
    return render_template(
        "library-detail.html",
        item=fetch_item(item_id),
        reviews=fetch_reviews(item_id),
        genres=GENRES,
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
    text = request.form.get("text")

    if text:
        add_review(item_id, text)

    return redirect(f"/library/item/{item_id}")


@app.route("/calendar")
def calendar():
    return render_template(
        "calendar.html",
        data=fetch_data(),
        life_events=fetch_life_events(),
        theme=session["theme"]
    )


@app.route("/calendar/event/add", methods=["POST"])
def calendar_event_add():
    title = request.form.get("title")
    emoji = request.form.get("emoji")
    event_date = request.form.get("event_date")
    description = request.form.get("description")

    if title and event_date:
        add_life_event(title, emoji, event_date, description)

    return redirect("/calendar")


@app.route("/achievements")
def achievements():
    return render_template(
        "achievements.html",
        categories=achievement_categories(),
        stats=life_stats(),
        theme=session["theme"]
    )

@app.route("/achievements/category/<category>")
def achievement_category(category):
    return render_template(
        "achievements.html",
        categories=achievement_categories(),
        achievements=achievements_by_category(category),
        selected_category=category,
        stats=life_stats(),
        theme=session["theme"]
    )

@app.route("/achievements/<achievement_id>")
def achievement_detail(achievement_id):
    achievement = find_achievement(achievement_id)

    return render_template(
        "achievement-detail.html",
        achievement=achievement,
        stats=life_stats(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        title = request.form.get("title")
        icon = request.form.get("icon")

        if title and icon:
            update_profile(title, icon)

        return redirect("/profile")

    return render_template(
        "profile.html",
        profile=get_profile(),
        titles=load_titles(),
        icons=load_icons(),
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


@app.route("/shop")
def shop():
    return render_template(
        "shop.html",
        shop_items=load_json("shop.json"),
        themes=load_themes(),
        owned=owned_themes(),
        profile=get_profile(),
        theme=session["theme"]
    )


@app.route("/shop/theme/<theme_class>/buy", methods=["POST"])
def shop_theme_buy(theme_class):
    buy_theme(theme_class)
    return redirect("/shop")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        selected_theme = request.form.get("theme")

        if selected_theme and is_owned(selected_theme):
            session["theme"] = selected_theme

        return redirect("/settings")

    return render_template(
        "settings.html",
        themes=load_themes(),
        owned=owned_themes(),
        current_theme=session["theme"],
        theme=session["theme"]
    )


@app.route("/goals")
def goals():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM goals ORDER BY created_at DESC")
    rows = c.fetchall()

    conn.close()

    return render_template("goals.html", goals=rows, theme=session["theme"])


@app.route("/goals/add", methods=["POST"])
def goals_add():
    title = request.form.get("title")

    if title:
        conn = connect()
        c = conn.cursor()

        c.execute("""
        INSERT INTO goals
        (id, title, done, created_at)
        VALUES (?, ?, 0, ?)
        """, (str(uuid.uuid4()), title, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    return redirect("/goals")


@app.route("/goals/done/<goal_id>", methods=["POST"])
def goals_done(goal_id):
    conn = connect()
    c = conn.cursor()

    c.execute("UPDATE goals SET done = 1 WHERE id = ?", (goal_id,))
    c.execute("UPDATE profile SET coins = coins + 10 WHERE id = 1")

    conn.commit()
    conn.close()

    return redirect("/goals")


@app.route("/shopping")
def shopping():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM shopping ORDER BY created_at DESC")
    rows = c.fetchall()

    conn.close()

    return render_template("shopping.html", items=rows, theme=session["theme"])


@app.route("/shopping/add", methods=["POST"])
def shopping_add():
    name = request.form.get("name")

    if name:
        conn = connect()
        c = conn.cursor()

        c.execute("""
        INSERT INTO shopping
        (id, name, done, created_at)
        VALUES (?, ?, 0, ?)
        """, (str(uuid.uuid4()), name, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    return redirect("/shopping")


@app.route("/shopping/done/<item_id>", methods=["POST"])
def shopping_done(item_id):
    conn = connect()
    c = conn.cursor()

    c.execute("UPDATE shopping SET done = 1 WHERE id = ?", (item_id,))
    c.execute("UPDATE profile SET coins = coins + 1 WHERE id = 1")

    conn.commit()
    conn.close()

    return redirect("/shopping")


@app.route("/test")
def test():
    return "OK"


if __name__ == "__main__":
    init()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)