from flask import Flask, request, redirect, url_for, render_template, session, flash
from db import init_db, get_saldo, add_expense, add_income, get_connection, start_travel, get_active_travel, add_travel_expense, get_travel_summary, close_active_travel,get_travel_history
import json
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
import re 
import smtplib
from email.mime.text import MIMEText
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
# SECRET KEY (attenzione: è "secret_key", non "security_key")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

#reset su email
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")  # meglio env
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_FROM"] = "Budget App <tuaccount@gmail.com>"


init_db()

def convert_to_eur_live(amount: float, currency: str) -> float:
    currency = currency.upper()

    if currency == "EUR":
        return round(amount, 2)

    try:
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={currency}&to=EUR"
        r = requests.get(url, timeout=3)
        data = r.json()

        # La API ritorna sempre nella forma data["rates"]["EUR"]
        rate_amount = data["rates"]["EUR"]
        return round(rate_amount, 2)

    except Exception as e:
        print("ERRORE conversione:", e)
        # fallback: non convertire
        return amount

def convert_from_eur_live(amount_eur: float, currency: str) -> float:
    currency = (currency or "EUR").upper()
    if currency == "EUR":
        return round(amount_eur, 2)
    try:
        url = f"https://api.frankfurter.app/latest?amount={amount_eur}&from=EUR&to={currency}"
        r = requests.get(url, timeout=3)
        data = r.json()
        value = data["rates"][currency]
        return round(float(value), 2)
    except Exception as e:
        print("ERRORE conversione da EUR:", e)
        return round(amount_eur, 2)

def send_reset_email(to_email, reset_link):
    subject = "Reset della password - Budget App"

    body = f"""
Ciao!

Hai richiesto di reimpostare la password del tuo account.
Per scegliere una nuova password, clicca sul link qui sotto (valido per 1 ora):

{reset_link}

Se non hai richiesto tu il reset, ignora questa mail.

A presto!
"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = app.config["MAIL_FROM"]
    msg["To"] = to_email

    try:
        if app.config.get("MAIL_USE_SSL", False):
            server = smtplib.SMTP_SSL(app.config["MAIL_SERVER"], app.config["MAIL_PORT"])
        else:
            server = smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"])

        server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()
        print("Email di reset inviata a", to_email)
    except Exception as e:
        print("ERRORE INVIO EMAIL RESET:", e)



# ------------------ REGISTRAZIONE ------------------ #

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()

        if not username or not password or not email:
            flash("Compila tutti i campi", "error")
            return redirect(url_for("register"))

        # controllo base formato email
        if not EMAIL_REGEX.match(email):
            flash("Inserisci un'email valida.", "error")
            return redirect(url_for("register"))

        conn = get_connection()
        cur = conn.cursor()

        password_hash = generate_password_hash(password)

        try:
            # INSERT con RETURNING id (PostgreSQL)
            cur.execute(
                """
                INSERT INTO users (username, password_hash, email)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (username, password_hash, email)
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

# ------------------ UTENTE -------------------#

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("Devi effettuare il login.", "error")
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        # 1) Aggiornamento email
        if action == "update_email":
            new_email = request.form.get("email", "").strip()

            if not new_email:
                conn.close()
                flash("Inserisci una email valida.", "error")
                return redirect(url_for("profile"))

            # controlla che non sia di un altro utente
            cur.execute(
                "SELECT id FROM users WHERE email = %s AND id != %s;",
                (new_email, user_id)
            )
            if cur.fetchone():
                conn.close()
                flash("Questa email è già usata da un altro account.", "error")
                return redirect(url_for("profile"))

            cur.execute(
                "UPDATE users SET email = %s WHERE id = %s;",
                (new_email, user_id)
            )
            conn.commit()
            conn.close()
            flash("Email aggiornata con successo.", "success")
            return redirect(url_for("profile"))

        # 2) Aggiornamento username
        elif action == "update_username":
            new_username = request.form.get("username", "").strip()

            if not new_username:
                conn.close()
                flash("Inserisci uno username valido.", "error")
                return redirect(url_for("profile"))

            # controlla che non sia di un altro
            cur.execute(
                "SELECT id FROM users WHERE username = %s AND id != %s;",
                (new_username, user_id)
            )
            if cur.fetchone():
                conn.close()
                flash("Questo username è già usato da un altro account.", "error")
                return redirect(url_for("profile"))

            cur.execute(
                "UPDATE users SET username = %s WHERE id = %s;",
                (new_username, user_id)
            )
            conn.commit()
            conn.close()
            flash("Username aggiornato con successo.", "success")
            return redirect(url_for("profile"))

        # 3) Cambio password
        elif action == "change_password":
            current_password = request.form.get("current_password", "").strip()
            new_password = request.form.get("new_password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()

            if not current_password or not new_password or not confirm_password:
                conn.close()
                flash("Compila tutti i campi per cambiare password.", "error")
                return redirect(url_for("profile"))

            # prendo l'hash attuale
            cur.execute(
                "SELECT password_hash FROM users WHERE id = %s;",
                (user_id,)
            )
            row = cur.fetchone()
            if not row:
                conn.close()
                flash("Utente non trovato.", "error")
                return redirect(url_for("login"))

            if not check_password_hash(row["password_hash"], current_password):
                conn.close()
                flash("La password attuale non è corretta.", "error")
                return redirect(url_for("profile"))

            if new_password != confirm_password:
                conn.close()
                flash("Le nuove password non coincidono.", "error")
                return redirect(url_for("profile"))

            new_hash = generate_password_hash(new_password)
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s;",
                (new_hash, user_id)
            )
            conn.commit()
            conn.close()
            flash("Password cambiata con successo.", "success")
            return redirect(url_for("profile"))

        # fallback
        conn.close()
        flash("Azione non valida.", "error")
        return redirect(url_for("profile"))

    # GET → carica dati utente
    cur.execute(
        "SELECT username, email FROM users WHERE id = %s;",
        (user_id,)
    )
    user = cur.fetchone()
    conn.close()

    return render_template("profile.html", user=user)

# -------------------- ELIMINA ------------------#

@app.route("/delete_account", methods=["POST"])
def delete_account():
    user_id = session.get("user_id")
    if not user_id:
        flash("Devi effettuare il login.", "error")
        return redirect(url_for("login"))

    confirm = request.form.get("confirm", "").strip()

    # per sicurezza facciamo scrivere ELIMINA
    if confirm != "ELIMINA":
        flash("Per eliminare l'account digita esattamente ELIMINA.", "error")
        return redirect(url_for("profile"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        # cancello l'utente; ON DELETE CASCADE pulirà accounts, travels, ecc.
        cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        conn.commit()
        conn.close()

        # svuoto la sessione
        session.clear()

        flash("Account eliminato correttamente. Ci dispiace vederti andare 😢", "success")
        return redirect(url_for("register"))

    except Exception as e:
        print("ERRORE DELETE_ACCOUNT:", e)
        conn.rollback()
        conn.close()
        flash("Errore durante l'eliminazione dell'account. Riprova.", "error")
        return redirect(url_for("profile"))



# ----------------- DIMENTICATA ---------------- #

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        if not email:
            flash("Inserisci una email.", "error")
            return redirect(url_for("forgot_password"))

        conn = get_connection()
        cur = conn.cursor()

        try:
            # cerco l'utente con questa email
            cur.execute("SELECT id FROM users WHERE email = %s;", (email,))
            row = cur.fetchone()

            if row:
                user_id = row["id"]

                # genero token e scadenza
                token = secrets.token_urlsafe(32)
                expires_at = datetime.utcnow() + timedelta(hours=1)

                cur.execute(
                    """
                    UPDATE users
                    SET reset_token = %s,
                        reset_token_expires_at = %s
                    WHERE id = %s;
                    """,
                    (token, expires_at, user_id)
                )
                conn.commit()

                # link assoluto tipo https://tuo-sito/reset_password?token=...
                reset_link = url_for("reset_password", token=token, _external=True)

                # invio email
                send_reset_email(email, reset_link)

            # NB: se l'email non esiste, non diciamo niente di diverso
            conn.close()

            flash("Se l'email è registrata, ti abbiamo inviato un link per il reset.", "success")
            return redirect(url_for("forgot_password"))

        except Exception as e:
            print("ERRORE FORGOT_PASSWORD:", e)
            conn.rollback()
            conn.close()
            flash("Errore durante la richiesta di reset. Riprova.", "error")
            return redirect(url_for("forgot_password"))

    # GET
    return render_template("forgot_password.html")

# ----------------- RESET ------------------#

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    # prendo il token dalla query (GET) o dal form (POST)
    if request.method == "GET":
        token = request.args.get("token", "").strip()
    else:
        token = request.form.get("token", "").strip()

    if not token:
        flash("Link di reset non valido.", "error")
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id, reset_token_expires_at
            FROM users
            WHERE reset_token = %s;
            """,
            (token,)
        )
        row = cur.fetchone()

        if not row:
            conn.close()
            flash("Link di reset non valido o già usato.", "error")
            return redirect(url_for("login"))

        user_id = row["id"]
        expires_at = row["reset_token_expires_at"]

        # controllo scadenza
        if not expires_at or expires_at < datetime.utcnow():
            conn.close()
            flash("Link di reset scaduto. Richiedine uno nuovo.", "error")
            return redirect(url_for("forgot_password"))

        # GET → mostro form nuova password
        if request.method == "GET":
            conn.close()
            return render_template("reset_password.html", token=token)

        # POST → salvo nuova password
        new_password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        if not new_password or not confirm:
            conn.close()
            flash("Compila tutti i campi.", "error")
            return redirect(url_for("reset_password", token=token))

        if new_password != confirm:
            conn.close()
            flash("Le password non coincidono.", "error")
            return redirect(url_for("reset_password", token=token))

        new_hash = generate_password_hash(new_password)

        cur.execute(
            """
            UPDATE users
            SET password_hash = %s,
                reset_token = NULL,
                reset_token_expires_at = NULL
            WHERE id = %s;
            """,
            (new_hash, user_id)
        )
        conn.commit()
        conn.close()

        flash("Password aggiornata con successo! Ora puoi fare il login.", "success")
        return redirect(url_for("login"))

    except Exception as e:
        print("ERRORE RESET_PASSWORD:", e)
        conn.rollback()
        conn.close()
        flash("Errore durante il reset della password. Riprova.", "error")
        return redirect(url_for("forgot_password"))



# ------------------ TIPO ------------------ #

@app.route("/tipo", methods=["GET", "POST"])
def tipo():
    # se invia il form (ha scelto una categoria)
    if request.method == "POST":
        category = request.form.get("category")
        
        #controllo se viaggio e reindirizzo
        if category == "viaggio":
            return redirect(url_for("viaggio"))

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


# ------------------ BUDGET ------------------ #

@app.route("/budget", methods=["GET", "POST"])
def budget():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    if request.method == "POST":
        amount_str = request.form.get("amount", "").replace(",", ".")
        try:
            amount = float(amount_str)
        except ValueError:
            flash("Importo non valido", "error")
            return redirect(url_for("budget"))

        if amount <= 0:
            flash("L'importo deve essere positivo", "error")
            return redirect(url_for("budget"))

        # Inizia un nuovo viaggio con questo budget
        start_travel(user_id, amount)
        return redirect(url_for("viaggio"))

    # GET: se c'è già un viaggio attivo, potresti anche reindirizzare
    active_travel = get_active_travel(user_id)
    current_budget = f"{active_travel['budget']:.2f}" if active_travel else "0.00"
    return render_template("budget.html", budget=current_budget)

# ------------------ VIAGGIO -------------------#

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


@app.route("/storico_viaggi")
def storico_viaggi():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    viaggi = get_travel_history(user_id)
    return render_template("storico_viaggi.html", viaggi=viaggi)

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

if __name__ == "__main__":
    app.run()



