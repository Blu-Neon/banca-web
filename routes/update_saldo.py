from flask import request, redirect, url_for, render_template, session, flash
from db import get_connection, get_saldo, add_expense, add_income
from app import app


@app.route("/update-saldo", methods=["GET", "POST"])
def update_saldo():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    if request.method == "POST":
        amount_str = request.form.get("amount", "").replace(",", ".")
        try:
            amount = float(amount_str)
        except ValueError:
            flash("Importo non valido", "error")
            return redirect(url_for("update_saldo"))

        if amount <= 0:
            flash("L'importo deve essere positivo", "error")
            return redirect(url_for("update_saldo"))

        add_income(user_id, amount)
        return redirect(url_for("home"))

    saldo = f"{get_saldo(user_id):.2f}"
    return render_template("expense.html", saldo=saldo)