from flask import request, redirect, url_for, render_template, session, flash
from db import (
    start_travel, get_active_travel, add_travel_expense,
    get_travel_summary, close_active_travel, get_travel_history,
    get_connection
)
from app import app, convert_to_eur_live, convert_from_eur_live


@app.route("/viaggio/chiudi", methods=["POST"])
def chiudi_viaggio():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    nome = request.form.get("nome_viaggio", "").strip() or None

    travel, total_spent, remaining = close_active_travel(user_id, nome)

    if not travel:
        flash("Nessun viaggio attivo da chiudere", "error")
        return redirect(url_for("viaggio"))

    # Messaggino riassuntivo (remaining può essere + o -)
    if remaining > 0:
        flash(f"Hai risparmiato {remaining:.2f}€, aggiunti al saldo 🎉", "success")
    elif remaining < 0:
        flash(f"Hai sforato il budget di {-remaining:.2f}€, tolti dal saldo 😅", "error")
    else:
        flash("Hai speso esattamente il budget!", "info")

    return redirect(url_for("storico_viaggi"))