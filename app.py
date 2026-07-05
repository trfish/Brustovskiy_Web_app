import sqlite3
import os
from flask import (
	Flask, request, redirect, url-for,
	render-template, render-template-string, make-response
)

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def init_db():
	conn = sqlite3.connect(DB_PATH)
	cur = conn.cursor()
	cur.execute("""
		CREATE TABLE IF NOT EXIST users (
			id	INTEGER	PRIMARY KEY	AUTOINCREMENT,
			username	TEXT	UNIQUE	NOT NULL,
			password	TEXT	NOT NULL
		)
	""")
	conn.commit()
	conn.close()

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.set("password", "")
