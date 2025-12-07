from flask import request, redirect, url_for, render_template, session, flash
from db import (
    start_travel, get_active_travel, add_travel_expense,
    get_travel_summary, close_active_travel, get_travel_history,
    get_connection
)
from app import app, convert_to_eur_live, convert_from_eur_live

@app.route("/budget", methods=["GET", "POST"])
def budget():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    if request.method == "POST":
        amount_str = request.form.get("amount", "").replace(",", ".")
        try:
            amount = float(amount_str)
        except ValueError:
            flash("Importo non valido", "error")
            return redirect(url_for("budget"))

        if amount <= 0:
            flash("L'importo deve essere positivo", "error")
            return redirect(url_for("budget"))

        # Inizia un nuovo viaggio con questo budget
        start_travel(user_id, amount)
        return redirect(url_for("viaggio"))

    # GET: se c'è già un viaggio attivo, potresti anche reindirizzare
    active_travel = get_active_travel(user_id)
    current_budget = f"{active_travel['budget']:.2f}" if active_travel else "0.00"
    return render_template("budget.html", budget=current_budget)