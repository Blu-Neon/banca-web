from flask import request, redirect, url_for, render_template, session, flash
from app import app
from db import (
    add_abbonamento,
    get_abbonamenti,
    applica_abbonamenti,
)

@app.route("/abbonamenti", methods=["GET", "POST"])
def abbonamenti():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # prima applico eventuali rinnovi dovuti oggi
    applica_abbonamenti(user_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        amount_str = request.form.get("amount", "").replace(",", ".")
        tipo = request.form.get("tipo")

        if not name or not amount_str or not tipo:
            flash("Compila tutti i campi e scegli mensile/annuale.", "error")
            return redirect(url_for("abbonamenti"))

        if tipo not in ("mensile", "annuale"):
            flash("Tipo abbonamento non valido.", "error")
            return redirect(url_for("abbonamenti"))

        try:
            amount = float(amount_str)
        except ValueError:
            flash("Importo non valido", "error")
            return redirect(url_for("abbonamenti"))

        if amount <= 0:
            flash("L'importo deve essere positivo", "error")
            return redirect(url_for("abbonamenti"))

        add_abbonamento(user_id, name, amount, tipo)
        flash("Abbonamento salvato.", "success")
        return redirect(url_for("abbonamenti"))

    # GET: lista + totali
    abbonamenti_list = get_abbonamenti(user_id)

    totale_mensile = sum(float(a["amount"]) for a in abbonamenti_list if a["tipo"] == "mensile")
    totale_annuale = sum(float(a["amount"]) for a in abbonamenti_list if a["tipo"] == "annuale")

    spesa_media_mensile = totale_mensile + (totale_annuale / 12.0)

    return render_template(
        "abbonamenti.html",
        abbonamenti=abbonamenti_list,
        totale_mensile=totale_mensile,
        totale_annuale=totale_annuale,
        spesa_media_mensile = spesa_media_mensile,
    )


@app.route("/abbonamenti/delete/<int:abb_id>", methods=["POST"])
def delete_abbonamento(abb_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]

    from db import get_connection
    conn = get_connection()
    cur = conn.cursor()

    # elimino solo se appartiene all'utente loggato
    cur.execute(
        """
        DELETE FROM abbonamenti
        WHERE abb_id = %s AND user_id = %s;
        """,
        (abb_id, user_id),
    )
    conn.commit()
    conn.close()

    flash("Abbonamento eliminato.", "success")
    return redirect(url_for("abbonamenti"))
