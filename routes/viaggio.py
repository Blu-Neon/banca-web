from flask import request, redirect, url_for, render_template, session, flash
from db import (
    start_travel, get_active_travel, add_travel_expense,
    get_travel_summary, close_active_travel, get_travel_history,
    get_connection
)
from app import app, convert_to_eur_live, convert_from_eur_live


@app.route("/viaggio", methods=["GET", "POST"])
def viaggio():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    # Se non c'è viaggio attivo → vai a budget
    active_travel = get_active_travel(user_id)
    if not active_travel:
        return redirect(url_for("budget"))

    # ---------- POST: REGISTRA SPESA ----------
    if request.method == "POST":
        amount_str = request.form.get("amount", "").replace(",", ".")
        category = request.form.get("category")
        currency = request.form.get("currency", "EUR")

        if not category:
            flash("Seleziona prima una categoria", "error")
            return redirect(url_for("viaggio"))

        # valida importo
        try:
            amount_foreign = float(amount_str)
        except ValueError:
            flash("Importo non valido", "error")
            return redirect(url_for("viaggio"))

        if amount_foreign <= 0:
            flash("L'importo deve essere positivo", "error")
            return redirect(url_for("viaggio"))

        # Conversione live in EUR
        amount_eur = convert_to_eur_live(amount_foreign, currency)

        # Salva spesa viaggio (EUR + valuta originale)
        add_travel_expense(
            user_id,
            amount_eur,
            category,
            original_amount=amount_foreign,
            original_currency=currency,
        )

        return redirect(url_for("viaggio"))

    # ---------- GET: MOSTRA RIEPILOGO VIAGGIO ----------
    travel, total_spent, per_category = get_travel_summary(user_id)

    # (Doppio check sicurezza)
    if not travel:
        return redirect(url_for("budget"))

    budget = float(travel["budget"])
    remaining = budget - total_spent

    display_currency = request.args.get("display_currency", "EUR").upper()
    remaining_display = convert_from_eur_live(remaining, display_currency)

    return render_template(
        "viaggio.html",
        budget=f"{budget:.2f}",
        total_spent=f"{total_spent:.2f}",
        remaining=f"{remaining:.2f}",
        per_category=per_category,
        display_currency=display_currency,
        remaining_display=f"{remaining_display:.2f}"
    )


