from flask import request, redirect, url_for, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from app import app
from permissions import PERM_XMAS, has_perm, PERM_ADMIN, PERM_MEDIA, PERM_PROGRAMMER


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
        "SELECT username, email, perms FROM users WHERE id = %s;",
        (user_id,)
    )
    user = cur.fetchone()
    conn.close()

    # Permessi 
    perms = int((user or {}).get("perms") or 0)
    is_admin = has_perm(perms, PERM_ADMIN)

    recognitions_all = [
        {
            "label": "Xmas",
            "href": url_for("xmas.xmas_card"),  # cliccabile
            "perm": PERM_XMAS,
            "type": "svg",  # useremo l’svg già presente nel template
        },
        {
            "label": "Media",
            "img": url_for("static", filename="badges/media-manager.png"),
            "perm": PERM_MEDIA,
        },
        {
            "label": "Programmer",
            "img": url_for("static", filename="badges/programmer.png"),
            "perm": PERM_PROGRAMMER,
        },
    ]

    recognitions = [
        r for r in recognitions_all
        if is_admin or has_perm(perms, r["perm"])
    ]

    return render_template("profile.html", user=user, recognitions=recognitions)
