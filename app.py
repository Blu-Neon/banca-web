from flask import Flask, request, redirect, url_for, render_template, session, flash
from db import init_db, get_saldo, add_expense, add_income, get_connection, start_travel, get_active_travel, add_travel_expense, get_travel_summary, close_active_travel,get_travel_history
import json
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
import re 
import secrets
from datetime import datetime, timedelta

# 475QZHTGNEQEEDJNXLYU7MRH
# Chiave APIqy3DnhIAHkvPQRB4

app = Flask(__name__)
# SECRET KEY (attenzione: è "secret_key", non "security_key")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


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
    api_key = os.environ.get("BREVO_API_KEY")
    sender = os.environ.get("MAIL_FROM")

    if not api_key or not sender:
        print("[BREVO] Non configurato. Invierei a:", to_email)
        print("[BREVO] LINK RESET:", reset_link)
        return

    url = "https://api.brevo.com/v3/smtp/email"

    data = {
        "sender": {"email": sender},
        "to": [{"email": to_email}],
        "subject": "Reset della password - Banca Utopia",
        "textContent": (
            "Ciao!\n\n"
            "Hai richiesto di reimpostare la password del tuo account.\n"
            f"Clicca qui per reimpostarla:\n{reset_link}\n\n"
            "Se non l'hai richiesta tu, ignora questa email."
        )
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    try:
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        if resp.status_code >= 300:
            print("[BREVO ERRORE]", resp.status_code, resp.text)
        else:
            print("[BREVO] Email inviata a", to_email)
    except Exception as e:
        print("[BREVO EXCEPTION]", e)
        print("[BREVO] LINK RESET (fallback):", reset_link)


from routes.register import *
from routes.login import *
from routes.logout import *
from routes.profile import *
from routes.delete_account import *
from routes.forgot_password import *
from routes.reset_password import *
from routes.tipo import *
from routes.home import *
from routes.add_expense import *
from routes.update_saldo import *
from routes.grafico import *
from routes.tipologia import *
from routes.storico import *
from routes.budget import *
from routes.viaggio import *
from routes.chiudi_viaggio import *
from routes.storico_viaggi import *
from routes.viaggio_spese import *


if __name__ == "__main__":
    app.run()



