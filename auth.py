from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, login_user
from werkzeug.security import check_password_hash

from models import User, db

bp = Blueprint("auth", __name__, url_prefix="/auth")

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    return db.session.get(User, user_id)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("library.index"))

    error = None
    username = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar_one_or_none()

        if user is None or not check_password_hash(
            user.password_hash, password
        ):
            error = "Invalid username or password"
        else:
            session.clear()
            login_user(user)
            return redirect(url_for("library.index"))

    return render_template(
        "auth/login.html",
        error=error,
        username=username,
    )