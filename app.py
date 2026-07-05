import sqlite3
import os
from flask import (
    Flask, request, redirect, url_for,
    render_template, render_template_string, make_response
)

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not username or not password:
            return render_template("register.html", error="Заполните все поля")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES ('%s', '%s')"
                % (username, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html",
                                   error="Такой пользователь уже существует")
        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        query = (
            "SELECT username FROM users "
            "WHERE username = '%s' AND password = '%s'" % (username, password)
        )
        cur.execute(query)
        row = cur.fetchone()
        conn.close()

        if row:
            logged_user = row[0]
            resp = make_response(redirect(url_for("welcome")))
            resp.set_cookie("username", logged_user)
            return resp

        return render_template("login.html", error="Неверный логин или пароль")

    return render_template("login.html")


@app.route("/welcome")
def welcome():
    username = request.cookies.get("username")

    if not username:
        return redirect(url_for("login"))

    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="utf-8">
        <title>Приветствие</title>
        <link rel="stylesheet" href="/static-style">
    </head>
    <body>
        <div class="card">
            <h1>Привет, {username}</h1>
            <a class="btn" href="/logout">Выйти</a>
        </div>
    </body>
    </html>
    """.format(username=username)
    return render_template_string(html)


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie("username", "", expires=0)
    return resp


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/static-style")
def static_style():
    css = """
    body{font-family:system-ui,Arial,sans-serif;background:#0f172a;
         display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
    .card{background:#1e293b;color:#e2e8f0;padding:40px 56px;border-radius:16px;
          text-align:center;box-shadow:0 10px 40px rgba(0,0,0,.4);}
    h1{margin:0 0 24px;font-size:28px;}
    .btn{display:inline-block;background:#3b82f6;color:#fff;text-decoration:none;
         padding:10px 22px;border-radius:8px;font-weight:600;}
    """
    resp = make_response(css)
    resp.headers["Content-Type"] = "text/css"
    return resp


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
