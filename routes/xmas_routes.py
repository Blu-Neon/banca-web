from __future__ import annotations

import os
from flask import Blueprint, abort, current_app, make_response, render_template, send_from_directory
from flask_login import current_user, login_required


xmas_bp = Blueprint("xmas", __name__)

# ✅ Set ONE of these to match your app
XMAS_ALLOWED_USER_ID = None     
XMAS_ALLOWED_EMAIL = tommaso.bossu@icloud.com      
XMAS_ALLOWED_USERNAME = None    


def _is_allowed() -> bool:
    if not current_user.is_authenticated:
        return False

    if XMAS_ALLOWED_USER_ID is not None:
        return getattr(current_user, "id", None) == XMAS_ALLOWED_USER_ID

    if XMAS_ALLOWED_EMAIL is not None:
        email = (getattr(current_user, "email", "") or "").lower()
        return email == XMAS_ALLOWED_EMAIL.lower()

    if XMAS_ALLOWED_USERNAME is not None:
        u = (getattr(current_user, "username", "") or "").lower()
        return u == XMAS_ALLOWED_USERNAME.lower()

    # If you forgot to set a rule, default deny.
    return False


@xmas_bp.route("/xmas-card")
@login_required
def xmas_card():
    if not _is_allowed():
        abort(403)
    return render_template("xmas_card.html")


@xmas_bp.route("/xmas-asset/<path:filename>")
@login_required
def xmas_asset(filename: str):
    if not _is_allowed():
        abort(403)

    # Put private files here:
    # instance/xmas_private/
    private_dir = os.path.join(current_app.instance_path, "xmas_private")

    resp = make_response(send_from_directory(private_dir, filename, as_attachment=False))
    # discourage caching (doesn't make it impossible to save, but helps a bit)
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Pragma"] = "no-cache"
    return resp
