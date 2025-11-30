from flask import Flask, request, redirect, url_for, render_template
from db import init_db, get_saldo, add_expense, add_income, get_connection
import json

app= Flask(__name__)

init_db()

@app.route("/", methods=["GET"])
def home():
    saldo = f"{get_saldo(1):.2f}"
    return render_template("home.html", saldo=saldo)

@app.route("/add-expense", methods=["POST"])
def add_expense_route():
    amount_str = request.form.get("amount", "").replace(",", ".")
    category = request.form.get("category", "altro")

    try:
        amount = float(amount_str)
    except ValueError:
        return redirect(url_for("home"))
    if amount <=0:
        return redirect(url_for("home"))
    add_expense(1, amount, category)
    return redirect(url_for("home"))


@app.route("/update-saldo", methods=["GET", "POST"])
def update_saldo():
    # Se arriva un POST → aggiorno il saldo e torno alla home
    if request.method == "POST":
        amount_str = request.form.get("amount", "").replace(",", ".")
        try:
            amount = float(amount_str)
        except ValueError:
            return redirect(url_for("update_saldo"))

        if amount <= 0:
            return redirect(url_for("update_saldo"))

        add_income(1, amount)
        return redirect(url_for("home"))

    # Se è un GET → mostro la pagina
    saldo = f"{get_saldo(1):.2f}"
    return render_template("expense.html", saldo=saldo)

@app.route("/grafico", methods=["GET"])
def grafico():
    cur = get_connection().cursor()

    # Movimenti del mese (entrate + spese), in ordine di data
    cur.execute("""
        SELECT amount, category, date
        FROM expenses
        WHERE user_id = 1
          AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        ORDER BY date ASC
    """)
    dati = cur.fetchall()

    # Ultimi 5 movimenti in assoluto (spese + entrate)
    cur.execute("""
        SELECT amount, category, date
        FROM expenses
        WHERE user_id = 1
        ORDER BY date DESC
        LIMIT 5
    """)
    ultime_cinque = cur.fetchall()

    # Etichette (solo la data, senza orario)
    labels = [row["date"].split(" ")[0] for row in dati]

    # Costruisco i movimenti con il segno:
    # - spesa    -> movimento NEGATIVO
    # - entrata  -> movimento POSITIVO
    movimenti = []
    for row in dati:
        amount = float(row["amount"])
        category = row["category"]
        if category == "entrata":
            movimenti.append(amount)     # entrata: +amount
        else:
            movimenti.append(-amount)    # spesa:   -amount

    saldo_attuale = get_saldo(1)

    # saldo_finale = saldo_inizio_mese + somma(movimenti)
    # => saldo_inizio_mese = saldo_finale - somma(movimenti)
    saldo_inizio_mese = saldo_attuale - sum(movimenti)

    valori_saldo = []
    saldo_prog = saldo_inizio_mese
    for movimento in movimenti:
        saldo_prog += movimento
        valori_saldo.append(round(saldo_prog, 2))

    # Costruisco la lista delle ultime 5 spese/movimenti in HTML
    ultime_cinque = []
    for row in ultime_cinque_rows:
        ultime_cinque.append({
            "amount": float(row["amount"]),
            "category": row["category"],
            "date": row["date"].split(" ")[0],
        })

    return render_templates(
        "grafico.html",
        labels=labels,
        vaori_saldo = valori_saldo,
        ultime_cinque = ultime_cinque,    
    )   


@app.route("/tipologia", methods=["GET"])
def tipologia():
    conn = get_connection()
    cur = conn.cursor()

    # Totale spese per categoria del mese (no entrate)
    cur.execute("""
        SELECT category, SUM(amount) AS totale
        FROM expenses
        WHERE user_id = 1
          AND category != 'entrata'
          AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        GROUP BY category
        ORDER BY totale DESC
    """)
    righe = cur.fetchall()
    conn.close()

    labels = [r["category"] for r in righe]
    values = [float(r["totale"]) for r in righe]

    base_colors = ["#FF6384", "#36A2EB", "#FFCE56",
                   "#4BC0C0", "#9966FF", "#FF9F40"]

    if len(labels) == 0:
        colors = []
    elif len(labels) <= len(base_colors):
        colors = base_colors[:len(labels)]
    else:
        ripetizioni = (len(labels) // len(base_colors)) + 1
        colors = (base_colors * ripetizioni)[:len(labels)]

    # Preparo lista categoria → colore → valore
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


@app.route("/storico", methods=["GET"])
def storico():
    conn = get_connection()
    cur = conn.cursor()

    # Totale spese (non entrate) per ogni mese dell'anno corrente
    cur.execute("""
        SELECT strftime('%Y-%m', date) AS ym,
               SUM(CASE WHEN category != 'entrata' THEN amount ELSE 0 END) AS totale
        FROM expenses
        WHERE user_id = 1
          AND strftime('%Y', date) = strftime('%Y', 'now')
        GROUP BY ym
        ORDER BY ym ASC;
    """)
    righe = cur.fetchall()
    conn.close()

    # Mappa numero mese -> nome mese in italiano
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
        totale = row["totale"] or 0.0
        year, month_num = ym.split("-")
        nome_mese = nomi_mesi.get(month_num, month_num)

        storico.append({
            "mese": nome_mese,
            "totale": float(totale),
        })

    return render_template("storico.html", storico=storico)


if __name__ == "__main__":
	app.run()

























