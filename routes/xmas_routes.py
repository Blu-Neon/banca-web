from flask import Blueprint, abort, current_app, make_response, render_template, send_from_directory, session
import os
from db import get_connection
from permissions import PERM_XMAS, has_perm

xmas_bp = Blueprint("xmas", __name__)

def _is_allowed():
    uid = session.get("user_id")
    if not uid:
        return False
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT perms FROM users WHERE id=%s;", (uid,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return has_perm(row.get("perms"), PERM_XMAS)

@xmas_bp.route("/xmas-card")
def xmas_card():
    if not _is_allowed():
        # 404 = non rivela che la pagina esiste (privacy)
        abort(404)
    return render_template("xmas_card.html")

@xmas_bp.route("/xmas-asset/<path:filename>")
def xmas_asset(filename):
    if not _is_allowed():
        abort(404)
    private_dir = os.path.join(current_app.instance_path, "xmas_private")
    resp = make_response(send_from_directory(private_dir, filename))
    resp.headers["Cache-Control"] = "no-store"
    return resp
