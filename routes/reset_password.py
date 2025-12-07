from flask import request, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import secrets
from db import get_connection
from app import app, send_reset_email


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
