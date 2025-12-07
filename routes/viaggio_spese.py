from flask import request, redirect, url_for, render_template, session, flash
from db import (
    start_travel, get_active_travel, add_travel_expense,
    get_travel_summary, close_active_travel, get_travel_history,
    get_connection
)
from app import app, convert_to_eur_live, convert_from_eur_live

@app.route("/viaggio/spese")
def viaggio_spese():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    # viaggio attivo
    active_travel = get_active_travel(user_id)
    if not active_travel:
        flash("Nessun viaggio attivo", "error")
        return redirect(url_for("budget"))

    travel_id = active_travel["id"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            category,
            amount,                -- in EUR
            original_amount,
            original_currency,
            created_at
        FROM travel_transactions
        WHERE travel_id = %s
        ORDER BY created_at DESC;
        """,
        (travel_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return render_template("viaggio_spese.html", spese=rows)