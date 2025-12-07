from flask import request, redirect, url_for, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from app import app


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