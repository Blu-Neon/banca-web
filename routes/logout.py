from flask import request, redirect, url_for, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from app import app, EMAIL_REGEX

@app.route("/logout")
def logout():
    session.clear()
    flash("Logout effettuato.", "success")
    return redirect(url_for("login"))