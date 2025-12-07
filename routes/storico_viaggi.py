from flask import request, redirect, url_for, render_template, session, flash
from db import (
    start_travel, get_active_travel, add_travel_expense,
    get_travel_summary, close_active_travel, get_travel_history,
    get_connection
)
from app import app, convert_to_eur_live, convert_from_eur_live


@app.route("/storico_viaggi")
def storico_viaggi():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    viaggi = get_travel_history(user_id)
    return render_template("storico_viaggi.html", viaggi=viaggi)