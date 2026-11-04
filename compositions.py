from types import SimpleNamespace

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.routing import BuildError

from models import Composition, Note, db
from render_service import composition_to_svg, empty_staff_svg

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

# Accidental choices in the palette: (value saved on the Note, button text, label).
# "" means "no accidental": the note follows the key signature (F in G major is F-sharp).
# "natural" is an explicit natural sign that cancels the key signature.
ACCIDENTALS = [
    ("", "Key", "Key signature"),
    ("natural", "♮", "Natural"),
    ("sharp", "♯", "Sharp"),
    ("flat", "♭", "Flat"),
]

# Order in which sharps and flats are added to major-key signatures.
SHARP_ORDER = "FCGDAEB"
FLAT_ORDER = "BEADGCF"
SHARP_KEYS = ["C major", "G major", "D major", "A major", "E major", "B major", "F# major", "C# major"]
FLAT_KEYS = ["C major", "F major", "Bb major", "Eb major", "Ab major", "Db major", "Gb major", "Cb major"]


def key_accidentals(key_signature):
    """Which letters a major key sharpens or flattens, e.g. "G major" -> {"F": "sharp"}."""
    if key_signature in SHARP_KEYS:
        return {letter: "sharp" for letter in SHARP_ORDER[:SHARP_KEYS.index(key_signature)]}
    if key_signature in FLAT_KEYS:
        return {letter: "flat" for letter in FLAT_ORDER[:FLAT_KEYS.index(key_signature)]}
    return {}


def effective_accidental(pitch, accidental, key_signature):
    """The accidental a note actually sounds with: its own, or else the key signature's."""
    return accidental or key_accidentals(key_signature).get(pitch, "")


# --- Treble-clef range check (US-04-T4, NTT-42) -------------------------------

# Semitones above C for each letter, and how far each accidental moves it.
LETTER_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
ACCIDENTAL_SEMITONES = {"": 0, "natural": 0, "sharp": 1, "flat": -1}
ACCIDENTAL_SYMBOLS = {"": "", "natural": "♮", "sharp": "♯", "flat": "♭"}


def midi_number(pitch, octave, accidental=""):
    """MIDI note number, e.g. C4 -> 60, A3 -> 57, A-flat 3 -> 56."""
    return (octave + 1) * 12 + LETTER_SEMITONES[pitch] + ACCIDENTAL_SEMITONES[accidental]


def note_range_error(pitch, octave, accidental, key_signature):
    """Error message if the note is outside the treble-clef range (A3 to C6), else None.

    Checks the note it actually becomes, so the key signature counts:
    A3 in E-flat major is A-flat 3, which is below the range.
    Rests have no pitch (pitch is None) and always pass.
    """
    if pitch is None:
        return None
    if pitch not in LETTER_SEMITONES:
        return "Choose a pitch from A to G."
    try:
        octave = int(octave)
    except (TypeError, ValueError):
        return "Choose an octave."
    if (accidental or "") not in ACCIDENTAL_SEMITONES:
        return "Choose a valid accidental."

    acc = effective_accidental(pitch, accidental or "", key_signature)
    note = midi_number(pitch, octave, acc)
    low = midi_number(*RANGE_LOW)
    high = midi_number(*RANGE_HIGH)
    if low <= note <= high:
        return None

    name = f"{pitch}{ACCIDENTAL_SYMBOLS[acc]}{octave}"
    span = f"{RANGE_LOW[0]}{RANGE_LOW[1]} to {RANGE_HIGH[0]}{RANGE_HIGH[1]}"
    where = "below" if note < low else "above"
    return f"{name} is {where} the treble-clef range ({span})."

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
    composition = get_owned_composition(composition_id)
    return render_editor(composition)


def get_owned_composition(composition_id):
    """Return the current user's composition, or 404 if missing/not owned.

    Call this before reading or changing an existing composition.
    Route handlers must also use @login_required.
    """
    composition = db.session.execute(
        db.select(Composition).where(
            Composition.id == composition_id,
            Composition.user_id == current_user.id,
        )
    ).scalar_one_or_none()

    if composition is None:
        abort(404)

    return composition


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


def staff_svg_for(composition):
    """Sheet-music SVG for the editor.

    A piece with notes gets its music (NTT-54); a new piece with no notes gets
    an empty staff with its clef, key, time signature and tempo (NTT-55).
    If drawing fails, the editor still opens: it returns None and the page
    shows a short message instead of an error page.
    """
    try:
        if getattr(composition, "notes", None):
            return composition_to_svg(composition)
        return empty_staff_svg(composition)
    except Exception:
        current_app.logger.exception("Could not draw composition %s", getattr(composition, "id", None))
        return None


def render_editor(composition, preview=False):
    return render_template(
        "compositions/editor.html",
        composition=composition,
        staff_svg=staff_svg_for(composition),
        pitches=PITCHES,
        octaves=OCTAVES,
        durations=DURATIONS,
        accidentals=ACCIDENTALS,
        key_acc=key_accidentals(getattr(composition, "key_signature", None)),
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

@bp.post("/<int:composition_id>/notes")
@login_required
def add_note(composition_id):
    composition = get_owned_composition(composition_id)

    duration = request.form.get("duration", "")
    is_rest = request.form.get("is_rest") == "1"
    pitch = request.form.get("pitch")
    octave = request.form.get("octave")
    accidental = request.form.get("accidental", "")

    error = None
    if duration not in dict(DURATIONS):
        error = "Choose a valid note duration."
    elif not is_rest:
        if not pitch:
            error = "Choose a pitch from A to G."
        else:
            error = note_range_error(
                pitch, octave, accidental, composition.key_signature
            )

    if error:
        flash(error, "error")
        return render_editor(composition), 400

    last_position = db.session.execute(
        db.select(db.func.max(Note.position)).where(
            Note.composition_id == composition.id
        )
    ).scalar_one()

    note = Note(
        composition_id=composition.id,
        position=1 if last_position is None else last_position + 1,
        pitch=None if is_rest else pitch,
        octave=None if is_rest else int(octave),
        duration=duration,
        accidental=None if is_rest else effective_accidental(
            pitch, accidental, composition.key_signature
        ),
        is_rest=is_rest,
    )
    db.session.add(note)
    db.session.commit()

    flash("Note added", "success")
    return redirect(
        url_for("compositions.editor", composition_id=composition.id)
    )
