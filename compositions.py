from types import SimpleNamespace

from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("compositions", __name__, url_prefix="/compositions")

PITCHES = ["C", "D", "E", "F", "G", "A", "B"]
OCTAVES = [3, 4, 5, 6]
DURATIONS = [("whole", "Whole"), ("half", "Half"), ("quarter", "Quarter"), ("eighth", "Eighth")]
ACCIDENTALS = [("", "♮", "Natural"), ("sharp", "♯", "Sharp"), ("flat", "♭", "Flat")]


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

NEW_FORM_DEFAULTS = {"title": "", "key_signature": "C major", "time_signature": "4/4", "tempo": TEMPO_DEFAULT}


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
        errors["tempo"] = f"Tempo must be a whole number from {TEMPO_MIN} to {TEMPO_MAX}."
    else:
        if TEMPO_MIN <= tempo <= TEMPO_MAX:
            values["tempo"] = tempo
        else:
            errors["tempo"] = f"Tempo must be between {TEMPO_MIN} and {TEMPO_MAX} BPM."

    return values, errors


def render_new_form(values=None, errors=None, status=200):
    """Render the new-composition form"""
    return render_template(
        "compositions/new.html",
        values={**NEW_FORM_DEFAULTS, **(values or {})},
        errors=errors or {},
        key_signatures=KEY_SIGNATURES,
        time_signatures=TIME_SIGNATURES,
        tempo_min=TEMPO_MIN, tempo_max=TEMPO_MAX,
        title_max=TITLE_MAX,
    ), status


# NTT-35 builds the form  
# NTT-36 adds POST to this same route:
@bp.get("/new")
@login_required
def new():
    return render_new_form()


def sample_composition():
    melody = ["E", "E", "F", "G", "G", "F", "E", "D"]
    notes = [
        SimpleNamespace(position=i, pitch=p, octave=4, duration="quarter", accidental=None, is_rest=False)
        for i, p in enumerate(melody, start=1)
    ]
    return SimpleNamespace(
        id=None, title="Ode to Joy", key_signature="C major",
        time_signature="4/4", tempo=100, notes=notes,
    )


def render_editor(composition, preview=False):
    return render_template(
        "compositions/editor.html",
        composition=composition,
        pitches=PITCHES, octaves=OCTAVES, durations=DURATIONS, accidentals=ACCIDENTALS,
        preview=preview,
    )


# TEMP (NTT-37):Point it at render_editor(). (NTT-36)
@bp.get("/preview")
def editor_preview():
    return render_editor(sample_composition(), preview=True)
