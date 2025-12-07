from flask import request, redirect, url_for, render_template, session, flash
from db import get_connection, get_saldo, add_expense, add_income
from app import app


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