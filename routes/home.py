from flask import request, redirect, url_for, render_template, session, flash
from db import get_connection, get_saldo, add_expense, add_income
from app import app

@app.route("/", methods=["GET"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    selected_category = session.get("selected_category")
    saldo = f"{get_saldo(user_id):.2f}"
    return render_template("home.html", saldo=saldo, username=session.get("username"), selected_category=selected_category)

