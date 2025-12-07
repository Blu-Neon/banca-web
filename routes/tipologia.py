from flask import request, redirect, url_for, render_template, session, flash
from db import get_connection, get_saldo, add_expense, add_income
from app import app


@app.route("/tipologia", methods=["GET"])
def tipologia():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    # Totale spese per categoria del mese (solo type = 'expense')
    cur.execute("""
        SELECT category, SUM(amount) AS totale
        FROM transactions
        WHERE user_id = %s
          AND type = 'expense'
          AND date_trunc('month', created_at) = date_trunc('month', CURRENT_DATE)
        GROUP BY category
        ORDER BY totale DESC
    """, (user_id,))
    righe = cur.fetchall()
    conn.close()

    category_colors = {
    "spesa":"#FF6384",
    "altro":"#595A5B",
    "evitabile":"#ED0909",
    "trasporti":"#4BC0C0",
    "ristorante":"#9966FF",
    "svago":"#36A2EF",
    "viaggio":"#6D0251",
    "vestiti":"#3AF083"
    }


    labels = [r["category"] for r in righe]
    values = [float(r["totale"]) for r in righe]

    # ["#FF6384", "#36A2EB", "#FFCE56","#4BC0C0", "#9966FF", "#FF9F40"]

    colors = [category_colors[cat] for cat in labels]

    legenda = []
    for cat, col, val in zip(labels, colors, values):
        legenda.append({
            "category": cat,
            "color": col,
            "value": val
        })

    return render_template(
        "tipologia.html",
        labels=labels,
        values=values,
        colors=colors,
        legenda=legenda
    )