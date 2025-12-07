from flask import request, redirect, url_for, render_template, session, flash
from db import get_connection, get_saldo, add_expense, add_income
from app import app


@app.route("/add-expense", methods=["POST"])
def add_expense_route():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    amount_str = request.form.get("amount", "").replace(",", ".")
    category = session.get("selected_category")

    if not category:
        flash("Seleziona prima una categoria", "error")
        return redirect(url_for("tipo"))

    try:
        amount = float(amount_str)
    except ValueError:
        flash("Importo non valido", "error")
        return redirect(url_for("home"))

    if amount <= 0:
        flash("L'importo deve essere positivo", "error")
        return redirect(url_for("home"))

    add_expense(user_id, amount, category)
    session.pop("selected_category", None)
    return redirect(url_for("home"))