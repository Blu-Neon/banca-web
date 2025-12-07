from flask import request, redirect, url_for, render_template, session, flash
from db import get_connection, get_saldo, add_expense, add_income
from app import app


@app.route("/storico", methods=["GET"])
def storico():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    # Totale spese (solo type='expense') per ogni mese dell'anno corrente
    cur.execute("""
        SELECT to_char(created_at, 'YYYY-MM') AS ym,
               SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS totale_spese,
               SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS totale_entrate
        FROM transactions
        WHERE user_id = %s
          AND date_part('year', created_at) = date_part('year', CURRENT_DATE)
        GROUP BY ym
        ORDER BY ym ASC;
    """, (user_id,))
    righe = cur.fetchall()
    conn.close()

    nomi_mesi = {
        "01": "Gennaio",
        "02": "Febbraio",
        "03": "Marzo",
        "04": "Aprile",
        "05": "Maggio",
        "06": "Giugno",
        "07": "Luglio",
        "08": "Agosto",
        "09": "Settembre",
        "10": "Ottobre",
        "11": "Novembre",
        "12": "Dicembre",
    }

    storico = []
    for row in righe:
        ym = row["ym"]          # tipo "2025-03"

        totale_spese = float(row["totale_spese"] or 0.0)
        totale_entrate = float(row["totale_entrate"] or 0.0)
        totale = round(totale_entrate - totale_spese, 2)
        year, month_num = ym.split("-")
        nome_mese = nomi_mesi.get(month_num, month_num)

        storico.append({
            "mese": nome_mese,
            "totale": float(totale),
        })

    return render_template("storico.html", storico=storico)