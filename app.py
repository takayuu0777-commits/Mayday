from flask import Flask, render_template, request, redirect, jsonify, session
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "brain-os"

DB = "brain.sqlite"

# =========================
# DB接続
# =========================
def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# 初期化
# =========================
def init_db():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id TEXT PRIMARY KEY,
        text TEXT,
        category TEXT,
        summary TEXT,
        created_at TEXT,
        date_key TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS library (
        id TEXT PRIMARY KEY,
        title TEXT,
        genre TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


@app.before_request
def set_theme():
    if "theme" not in session:
        session["theme"] = "soft"


# =========================
# ログ機能
# =========================
def classify(text):
    if "仕事" in text:
        return "仕事"
    if "勉強" in text:
        return "学習"
    if "映画" in text or "漫画" in text:
        return "メディア"
    return "思考"


def summarize(text):
    return text[:40]


def save_log(text):
    conn = db()
    c = conn.cursor()

    now = datetime.now()

    c.execute("""
    INSERT INTO logs VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        text,
        classify(text),
        summarize(text),
        now.isoformat(),
        now.strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()


def fetch_logs():
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


# =========================
# 検索
# =========================
def search_logs(q):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM logs WHERE text LIKE ?", (f"%{q}%",))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================
# Library
# =========================
def fetch_library():
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM library")
    rows = c.fetchall()
    conn.close()

    data = {}
    for r in rows:
        g = r["genre"]
        data.setdefault(g, []).append(r["title"])

    for k in data:
        data[k].sort()

    return data


# =========================
# Calendar
# =========================
def calendar_data():
    conn = db()
    c = conn.cursor()
    c.execute("SELECT date_key, category FROM logs")
    rows = c.fetchall()
    conn.close()

    data = {}
    for r in rows:
        d = r["date_key"]
        cat = r["category"]
        data.setdefault(d, {})
        data[d][cat] = data[d].get(cat, 0) + 1

    return data


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("home.html", logs=fetch_logs(), theme=session["theme"])


@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("text")
    if text:
        save_log(text)
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
    return render_template("library.html", data=fetch_library(), theme=session["theme"])


@app.route("/calendar")
def calendar():
    return render_template("calendar.html", data=calendar_data(), theme=session["theme"])


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        session["theme"] = request.form.get("theme")
        return redirect("/settings")

    return render_template("settings.html", theme=session["theme"])


# =========================
# 起動（これ1個だけ）
# =========================
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)