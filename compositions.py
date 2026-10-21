from types import SimpleNamespace

from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("compositions", __name__, url_prefix="/compositions")

PITCHES = ["C", "D", "E", "F", "G", "A", "B"]
OCTAVES = [3, 4, 5, 6]
DURATIONS = [("whole", "Whole"), ("half", "Half"), ("quarter", "Quarter"), ("eighth", "Eighth")]
ACCIDENTALS = [("", "♮", "Natural"), ("sharp", "♯", "Sharp"), ("flat", "♭", "Flat")]


def sample_composition():
    """Made-up composition for the editor preview until real ones exist (US-03)."""
    melody = ["E", "E", "F", "G", "G", "F", "E", "D"]
    notes = [
        SimpleNamespace(position=i, pitch=p, octave=4, duration="quarter", accidental=None, is_rest=False)
        for i, p in enumerate(melody, start=1)
    ]
    return SimpleNamespace(
        id=None, title="Ode to Joy (opening)", key_signature="C major",
        time_signature="4/4", tempo=100, notes=notes,
    )


def render_editor(composition, preview=False):
    return render_template(
        "compositions/editor.html",
        composition=composition,
        pitches=PITCHES, octaves=OCTAVES, durations=DURATIONS, accidentals=ACCIDENTALS,
        preview=preview,
    )


# TEMPORARY (NTT-37): Remove once /compositions/<id> exists (NTT-36) and point it at render_editor().
@bp.get("/preview")
@login_required
def editor_preview():
    return render_editor(sample_composition(), preview=True)
