
import re

from flask import Blueprint, render_template, request,redirect
from flask_login import login_user
from models import User, db
from werkzeug.security import generate_password_hash

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    error = None

    if not username or not email or not password:
        error = "All fields are required."
    elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        error = "Please enter a valid email address."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."
    elif User.query.filter_by(username=username).first():
        error = "Username already exists."
    elif User.query.filter_by(email=email).first():
        error = "Email already exists."

    if error:
        return render_template("auth/register.html", error=error), 200

    
    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
   
    return redirect("/")
