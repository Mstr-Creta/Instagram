
import os
import sqlite3
from pathlib import Path
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "phishtrace.db"

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lab_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                username TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
                    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            )
        """)

        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(lab_events)"
            ).fetchall()
        }

        if "username" not in columns:
            conn.execute("""
                ALTER TABLE lab_events
                ADD COLUMN username TEXT NOT NULL DEFAULT ''
            """)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_ok"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)

    return wrapper


@app.route("/", methods=["GET"])
def index():
    return render_template("login.html")


@app.route("/submit", methods=["POST"])
def submit():
    # Accept only the declared training fields.
    email = request.form.get("email", "").strip()
    username = request.form.get("username", "").strip()

    if not email or not username:
        return render_template(
            "login.html",
            error="Test email and username are required."
        ), 400

    # Save the test data to the same database used by the admin page.
    with db() as conn:
        conn.execute(
            """
            INSERT INTO lab_events (email, username)
            VALUES (?, ?)
            """,
            (email, username),
        )

    return render_template(
        "submission_success.html"
    ), 200


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        submitted_password = request.form.get("password", "")

        if ADMIN_PASSWORD and submitted_password == ADMIN_PASSWORD:
            session.clear()
            session["admin_ok"] = True
            return redirect(url_for("admin_records"))

        error = "Invalid admin password or missing configuration."

    return render_template("admin_login.html", error=error)


@app.route("/admin/records", methods=["GET"])
@admin_required
def admin_records():
    with db() as conn:
        rows = conn.execute("""
            SELECT id, email, username, created_at
            FROM lab_events
            ORDER BY id DESC
        """).fetchall()

    return render_template("records.html", rows=rows)


@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    if not app.secret_key or not ADMIN_PASSWORD:
        raise RuntimeError(
            "Set FLASK_SECRET_KEY and ADMIN_PASSWORD "
            "environment variables before starting."
        )

    init_db()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )
