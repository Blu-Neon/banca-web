from flask import request, redirect, url_for, render_template, session, flash
from db import get_connection, get_saldo, add_expense, add_income
from app import app


@app.route("/grafico", methods=["GET"])
def grafico():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    # Movimenti del mese (entrate + spese), in ordine di data
    cur.execute("""
        SELECT amount, category, type, created_at
        FROM transactions
        WHERE user_id = %s
          AND date_trunc('month', created_at) = date_trunc('month', CURRENT_DATE)
        ORDER BY created_at ASC
    """, (user_id,))
    dati = cur.fetchall()

    # Ultimi 5 movimenti in assoluto (entrate + spese)
    cur.execute("""
        SELECT amount, category, type, created_at
        FROM transactions
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,))
    ultime_cinque_rows = cur.fetchall()

    conn.close()

    # Etichette (solo la data, senza orario)
    labels = []
    for row in dati:
        # created_at è un datetime di Postgres
        dt = row["created_at"]
        try:
            labels.append(dt.date().isoformat())
        except AttributeError:
            # nel dubbio, fallback a stringa
            labels.append(str(dt).split(" ")[0])

    # Movimenti con il segno
    movimenti = []
    for row in dati:
        amount = float(row["amount"])
        tipo = row["type"]
        if tipo == "income":
            movimenti.append(amount)      # entrata +
        else:
            movimenti.append(-amount)     # spesa -

    saldo_attuale = get_saldo(user_id)
    saldo_inizio_mese = saldo_attuale - sum(movimenti) if movimenti else saldo_attuale

    valori_saldo = []
    saldo_prog = saldo_inizio_mese
    for movimento in movimenti:
        saldo_prog += movimento
        valori_saldo.append(round(saldo_prog, 2))

    # Ultime 5 per il template
    ultime_cinque = []
    for row in ultime_cinque_rows:
        dt = row["created_at"]
        try:
            data_str = dt.date().isoformat()
        except AttributeError:
            data_str = str(dt).split(" ")[0]

        ultime_cinque.append({
            "amount": float(row["amount"]),
            "category": row["category"],
            "type": row["type"],
            "date": data_str,
        })

    return render_template(
        "grafico.html",
        labels=labels,
        valori_saldo=valori_saldo,
        ultime_cinque=ultime_cinque,
    )
