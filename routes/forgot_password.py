from flask import request, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import secrets
from db import get_connection
from app import app, send_reset_email


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