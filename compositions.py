from types import SimpleNamespace

from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.routing import BuildError

from models import Composition, db

bp = Blueprint("compositions", __name__, url_prefix="/compositions")

PITCHES = ["C", "D", "E", "F", "G", "A", "B"]
OCTAVES = [3, 4, 5, 6]
DURATIONS = [
    ("whole", "Whole"),
    ("half", "Half"),
    ("quarter", "Quarter"),
    ("eighth", "Eighth"),
    ("16th", "Sixteenth"),
]
# Treble-clef range (US-04): lowest and highest note the palette offers.
# The palette greys out pitches outside it; the add-note route (NTT-41/42)
# still validates on the server.
RANGE_LOW = ("A", 3)
RANGE_HIGH = ("C", 6)

ACCIDENTALS = [
    ("", "♮", "Natural"),
    ("sharp", "♯", "Sharp"),
    ("flat", "♭", "Flat"),
]

KEY_SIGNATURES = [
    ("C major", "C major"),
    ("G major", "G major (1\u266f)"),
    ("D major", "D major (2\u266f)"),
    ("A major", "A major (3\u266f)"),
    ("E major", "E major (4\u266f)"),
    ("B major", "B major (5\u266f)"),
    ("F# major", "F\u266f major (6\u266f)"),
    ("C# major", "C\u266f major (7\u266f)"),
    ("F major", "F major (1\u266d)"),
    ("Bb major", "B\u266d major (2\u266d)"),
    ("Eb major", "E\u266d major (3\u266d)"),
    ("Ab major", "A\u266d major (4\u266d)"),
    ("Db major", "D\u266d major (5\u266d)"),
    ("Gb major", "G\u266d major (6\u266d)"),
    ("Cb major", "C\u266d major (7\u266d)"),
]

TIME_SIGNATURES = ["2/4", "3/4", "4/4", "6/8"]
TEMPO_MIN, TEMPO_MAX, TEMPO_DEFAULT = 40, 240, 100
TITLE_MAX = 200

NEW_FORM_DEFAULTS = {
    "title": "",
    "key_signature": "C major",
    "time_signature": "4/4",
    "tempo": TEMPO_DEFAULT,
}


def validate_new_composition(form):
    """Check the new-composition form. Returns (values, errors)."""
    values = {
        "title": (form.get("title") or "").strip(),
        "key_signature": form.get("key_signature") or "",
        "time_signature": form.get("time_signature") or "",
        "tempo": (form.get("tempo") or "").strip(),
    }
    errors = {}

    if not values["title"]:
        errors["title"] = "Please give your piece a title."
    elif len(values["title"]) > TITLE_MAX:
        errors["title"] = f"Title must be {TITLE_MAX} characters or fewer."

    if values["key_signature"] not in dict(KEY_SIGNATURES):
        errors["key_signature"] = "Please choose a key."

    if values["time_signature"] not in TIME_SIGNATURES:
        errors["time_signature"] = "Please choose a time signature."

    try:
        tempo = int(values["tempo"])
    except ValueError:
        errors["tempo"] = (
            f"Tempo must be a whole number from {TEMPO_MIN} to {TEMPO_MAX}."
        )
    else:
        if TEMPO_MIN <= tempo <= TEMPO_MAX:
            values["tempo"] = tempo
        else:
            errors["tempo"] = (
                f"Tempo must be between {TEMPO_MIN} and {TEMPO_MAX} BPM."
            )

    return values, errors


def render_new_form(values=None, errors=None, status=200):
    """Render the new-composition form."""
    return render_template(
        "compositions/new.html",
        values={**NEW_FORM_DEFAULTS, **(values or {})},
        errors=errors or {},
        key_signatures=KEY_SIGNATURES,
        time_signatures=TIME_SIGNATURES,
        tempo_min=TEMPO_MIN,
        tempo_max=TEMPO_MAX,
        title_max=TITLE_MAX,
    ), status


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        values, errors = validate_new_composition(request.form)

        if errors:
            return render_new_form(values, errors, status=400)

        composition = Composition(
            title=values["title"],
            key_signature=values["key_signature"],
            time_signature=values["time_signature"],
            tempo=values["tempo"],
            user_id=current_user.id,
        )
        db.session.add(composition)
        db.session.commit()

        return redirect(
            url_for("compositions.editor", composition_id=composition.id)
        )

    return render_new_form()


@bp.get("/<int:composition_id>")
@login_required
def editor(composition_id):
    composition = db.session.execute(
        db.select(Composition).where(
            Composition.id == composition_id,
            Composition.user_id == current_user.id,
        )
    ).scalar_one_or_none()

    if composition is None:
        abort(404)

    return render_editor(composition)


def sample_composition():
    melody = ["E", "E", "F", "G", "G", "F", "E", "D"]
    notes = [
        SimpleNamespace(
            position=i,
            pitch=p,
            octave=4,
            duration="quarter",
            accidental=None,
            is_rest=False,
        )
        for i, p in enumerate(melody, start=1)
    ]
    return SimpleNamespace(
        id=None,
        title="Ode to Joy (opening)",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
        notes=notes,
    )


def add_note_url(composition):
    """URL the palette posts to, or None until the add-note route (NTT-41) exists.

    The route is expected at endpoint ``compositions.add_note`` taking
    ``composition_id``. Until it is registered, the Add note button stays disabled.
    """
    if getattr(composition, "id", None) is None:
        return None
    try:
        return url_for("compositions.add_note", composition_id=composition.id)
    except BuildError:
        return None


def render_editor(composition, preview=False):
    return render_template(
        "compositions/editor.html",
        composition=composition,
        pitches=PITCHES,
        octaves=OCTAVES,
        durations=DURATIONS,
        accidentals=ACCIDENTALS,
        range_low=RANGE_LOW,
        range_high=RANGE_HIGH,
        add_note_url=None if preview else add_note_url(composition),
        preview=preview,
    )


# Keep the sample preview available for existing editor tests.
@bp.get("/preview")
@login_required
def editor_preview():
    return render_editor(sample_composition(), preview=True)