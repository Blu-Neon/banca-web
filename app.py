from flask import Flask, request, redirect, url_for, render_template, session, flash
from db import init_db, get_saldo, add_expense, add_income, get_connection
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# SECRET KEY (attenzione: è "secret_key", non "security_key")
app.secret_key = "171dad4fceec506d4829140f5bb5de4fd96007236912e23267b05eafcdf7e6a7"

init_db()


# ------------------ REGISTRAZIONE ------------------ #

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Compila tutti i campi", "error")
            return redirect(url_for("register"))

        conn = get_connection()
        cur = conn.cursor()

        password_hash = generate_password_hash(password)

        try:
            # INSERT con RETURNING id (PostgreSQL)
            cur.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                RETURNING id;
                """,
                (username, password_hash)
            )
            row = cur.fetchone()
            user_id = row["id"]

            # crea account collegato
            cur.execute(
                "INSERT INTO accounts (user_id, saldo) VALUES (%s, 0);",
                (user_id,)
            )

            conn.commit()
        except Exception as e:
            conn.close()
            print("ERRORE REGISTER:", e)
            flash("Username già esistente o altro errore, riprova", "error")
            return redirect(url_for("register"))

        conn.close()
        flash("Registrazione completata! Ora puoi fare il login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ------------------ LOGIN / LOGOUT ------------------ #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM users WHERE username = %s;",
            (username,)
        )
        row = cur.fetchone()
        conn.close()

        if row is None:
            flash("Username non trovato", "error")
            return redirect(url_for("login"))

        user_id = row["id"]
        password_hash = row["password_hash"]

        if not check_password_hash(password_hash, password):
            flash("Password errata", "error")
            return redirect(url_for("login"))

        # login ok
        session["user_id"] = user_id
        session["username"] = username
        flash("Login effettuato!", "success")
        return redirect(url_for("tipo"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logout effettuato.", "success")
    return redirect(url_for("login"))

# ------------------ TIPO ------------------ #

@app.route("/tipo", methods=["GET", "POST"])
def tipo():
    # se invia il form (ha scelto una categoria)
    if request.method == "POST":
        category = request.form.get("category")
        session["selected_category"] = category   # la salvo in sessione
        return redirect(url_for("home"))         # vado alla home per inserire l'importo

    # se arriva in GET (prima volta dopo login)
    return render_template("tipo.html")

# ------------------ HOME ------------------ #

@app.route("/", methods=["GET"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    selected_category = session.get("selected_category")
    saldo = f"{get_saldo(user_id):.2f}"
    return render_template("home.html", saldo=saldo, username=session.get("username"), selected_category=selected_category)


# ------------------ AGGIUNTA SPESA ------------------ #

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


# ------------------ AGGIORNA SALDO (ENTRATE) ------------------ #

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


# ------------------ GRAFICO ------------------ #

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


# ------------------ TIPOLOGIA ------------------ #

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
    "evitabile":"#FFCE56",
    "trasporti":"#4BC0C0",
    "ristorante":"#9966FF",
    "svago":"#36A2EF",
    "viaggio":"#FFA34E",
    "vestiti":"#FF43FF"
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

# ------------------ STORICO ------------------ #

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

if __name__ == "__main__":
    app.run()



