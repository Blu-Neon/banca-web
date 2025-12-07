from flask import request, redirect, url_for, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from app import app, EMAIL_REGEX


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