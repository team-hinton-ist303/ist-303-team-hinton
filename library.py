from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models import Composition, db

bp = Blueprint("library", __name__, url_prefix="/library")


@bp.get("/")
@login_required
def index():
    compositions = db.session.execute(
        db.select(Composition)
        .where(Composition.user_id == current_user.id)
        .order_by(Composition.id.desc())
    ).scalars().all()

    return render_template(
        "library/index.html",
        compositions=compositions,
    )