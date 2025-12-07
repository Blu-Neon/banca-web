from flask import request, redirect, url_for, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from app import app, EMAIL_REGEX

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM users WHERE username = %s;",
            (username,)
        )
        row = cur.fetchone()
        conn.close()

        if row is None:
            flash("Username non trovato", "error")
            return redirect(url_for("login"))

        user_id = row["id"]
        password_hash = row["password_hash"]

        if not check_password_hash(password_hash, password):
            flash("Password errata", "error")
            return redirect(url_for("login"))

        # login ok
        session["user_id"] = user_id
        session["username"] = username
        flash("Login effettuato!", "success")
        return redirect(url_for("tipo"))

    return render_template("login.html")