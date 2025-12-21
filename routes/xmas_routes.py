from __future__ import annotations

import os
from flask import Blueprint, abort, current_app, make_response, render_template, send_from_directory



xmas_bp = Blueprint("xmas", __name__)

# ✅ Set ONE of these to match your app 
XMAS_ALLOWED_EMAIL = "tommaso.bossu@icloud.com".lower()     

def _get_logged_email() -> str:
    """
    Prova a leggere l'email dalla sessione.
    Cambia/aggiungi chiavi se nel tuo progetto usi un nome diverso.
    """
    for key in ("email", "user_email", "mail", "userMail"):
        v = session.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip().lower()
    return ""

def _is_allowed() -> bool:
    return _get_logged_email() == XMAS_ALLOWED_EMAIL

@xmas_bp.route("/xmas-card")
def xmas_card():
    if not _is_allowed():
        abort(403)
    return render_template("xmas_card.html")

@xmas_bp.route("/xmas-asset/<path:filename>")
def xmas_asset(filename: str):
    if not _is_allowed():
        abort(403)

    private_dir = os.path.join(current_app.instance_path, "xmas_private")
    resp = make_response(send_from_directory(private_dir, filename, as_attachment=False))
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Pragma"] = "no-cache"
    return resp
