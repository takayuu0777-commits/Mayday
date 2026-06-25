from flask import Flask, render_template, request, redirect, jsonify, session
import os

from modules.database import init
from modules.logs import save, fetch_all
from modules.search import search_logs
from modules.library import fetch_grouped
from modules.calendar import fetch_data
from modules.stats import life_stats

app = Flask(__name__)
app.secret_key = "brain-os"


@app.before_request
def before():
    init()

    if "theme" not in session:
        session["theme"] = "soft"


@app.route("/")
def home():
    return render_template(
        "home.html",
        logs=fetch_all(),
        stats=life_stats(),
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
        theme=session["theme"]
    )


@app.route("/calendar")
def calendar():
    return render_template(
        "calendar.html",
        data=fetch_data(),
        theme=session["theme"]
    )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        session["theme"] = request.form.get("theme")
        return redirect("/settings")

    return render_template(
        "settings.html",
        theme=session["theme"]
    )


@app.route("/test")
def test():
    return "OK"


if __name__ == "__main__":
    init()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)