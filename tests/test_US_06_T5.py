"""Tests for US-06-T5 (NTT-56): the sheet music SVG.

Task: one SVG note element per note, rests, key and time signature.

Acceptance criteria covered (from story US-06, NTT-8):
  - The editor shows a five-line staff with a treble clef, key signature, and time signature.
  - Each note sits on the correct line or space with the correct head, stem, and flag
    for its duration; accidentals are shown.
  - Bar lines appear where each measure fills up for the chosen time signature.
  - The staff updates right after a note or rest is added.
  - The SVG is generated on the server in Python.

Notes are added through the real add-note route, then the SVG is read from the
editor page. Verovio draws symbols from the SMuFL music font, so each symbol is
checked by its SMuFL code (for example E050 is the treble clef).

music21 splits a note or rest that crosses a bar line into two tied pieces, so
these tests keep each note inside one bar to keep the counts exact.

The staff for an empty piece (NTT-55) is still in review and is not tested here yet.
"""
import math
import re
import xml.etree.ElementTree as ET

import pytest

from compositions import KEY_SIGNATURES, TIME_SIGNATURES, key_accidentals
from models import Composition, db

SVG_NS = "{http://www.w3.org/2000/svg}"
LETTERS = "CDEFGAB"

# SMuFL codes Verovio uses for each symbol
TREBLE_CLEF = "E050"
ACCIDENTAL_GLYPHS = {"flat": "E260", "natural": "E261", "sharp": "E262"}
NOTEHEADS = {"whole": "E0A2", "half": "E0A3", "quarter": "E0A4", "eighth": "E0A4", "16th": "E0A4"}
FLAGS = {"eighth": {"E240", "E241"}, "16th": {"E242", "E243"}}   # stem up / stem down
RESTS = {"whole": "E4E3", "half": "E4E4", "quarter": "E4E5", "eighth": "E4E6", "16th": "E4E7"}
BEATS = {"whole": 4, "half": 2, "quarter": 1, "eighth": 0.5, "16th": 0.25}


def digit(n):
    return f"E08{n}"


# --- Helpers ------------------------------------------------------------------

@pytest.fixture
def make_piece(logged_in_client, test_user):
    """Create a piece owned by the logged-in user and add notes through the real route.

    notes: (pitch, octave, duration, accidental) tuples; pitch None means a rest.
    Returns the SVG the editor page shows.
    """
    def build(notes, key="C major", time_signature="4/4"):
        piece = Composition(user_id=test_user.id, title="SVG test", key_signature=key,
                            time_signature=time_signature, tempo=100)
        db.session.add(piece)
        db.session.commit()
        for pitch, octave, duration, accidental in notes:
            data = ({"is_rest": "1", "duration": duration} if pitch is None else
                    {"pitch": pitch, "octave": str(octave), "duration": duration,
                     "accidental": accidental})
            response = logged_in_client.post(f"/compositions/{piece.id}/notes", data=data)
            assert response.status_code == 302, (pitch, octave, duration, accidental)
        return editor_svg(logged_in_client, piece.id)
    return build


def editor_svg(client, piece_id):
    html = client.get(f"/compositions/{piece_id}").get_data(as_text=True)
    # Verovio nests an inner <svg>, so take everything up to the last closing tag.
    match = re.search(r'<div class="staff-svg">\s*(<svg.*</svg>)\s*</div>', html, re.S)
    assert match, "the editor page has no sheet music SVG"
    return match.group(1)


def note(pitch, octave=4, duration="quarter", accidental=""):
    return (pitch, octave, duration, accidental)


def rest(duration="quarter"):
    return (None, None, duration, "")


def classes(element):
    return (element.get("class") or "").split()


def groups(svg, name):
    """Every <g> element with this class, in drawing order."""
    return [e for e in ET.fromstring(svg).iter(SVG_NS + "g") if name in classes(e)]


def glyphs(element):
    """SMuFL codes used inside an element, in order."""
    return [re.search(r"#(E[0-9A-F]{3})", u.get("{http://www.w3.org/1999/xlink}href")).group(1)
            for u in element.iter(SVG_NS + "use")]


def child_groups(element, name):
    return [e for e in element.iter(SVG_NS + "g") if name in classes(e)]


def notes_and_rests(svg):
    """'note' / 'rest' in drawing order; a whole-bar rest (mRest) counts as a rest."""
    found = [e for e in ET.fromstring(svg).iter(SVG_NS + "g")
             if {"note", "rest", "mRest"} & set(classes(e))]
    return ["note" if "note" in classes(e) else "rest" for e in found]


def staff_lines(staff):
    """y positions of the staff's own lines (not ledger lines)."""
    return sorted(float(p.get("d").split()[1]) for p in staff if p.tag == SVG_NS + "path")


def notehead_y(note_group):
    head = child_groups(note_group, "notehead")[0]
    use = next(head.iter(SVG_NS + "use"))
    return float(re.search(r"translate\([^,]+,\s*([-\d.]+)", use.get("transform")).group(1))


# --- Staff and clef -----------------------------------------------------------

def test_staff_has_five_lines(make_piece):
    svg = make_piece([note("C"), note("E"), note("G")])

    staves = groups(svg, "staff")
    assert staves
    assert all(len(staff_lines(staff)) == 5 for staff in staves)


def test_staff_has_a_treble_clef(make_piece):
    svg = make_piece([note("C")])

    clefs = groups(svg, "clef")
    assert len(clefs) == 1
    assert glyphs(clefs[0]) == [TREBLE_CLEF]


def test_svg_is_drawn_on_the_server_into_the_page(make_piece):
    svg = make_piece([note("C")])
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")


# --- One SVG note element per note --------------------------------------------

@pytest.mark.parametrize("count", [1, 4, 8])
def test_one_svg_note_element_per_note(make_piece, count):
    svg = make_piece([note("C")] * count)
    assert len(groups(svg, "note")) == count


@pytest.mark.parametrize("pitch, octave", [
    (letter, octave) for octave in (3, 4, 5, 6) for letter in LETTERS
    if (3, 5) <= (octave, LETTERS.index(letter)) <= (6, 0)      # A3 to C6
])
def test_note_sits_on_the_correct_line_or_space(make_piece, pitch, octave):
    """Each step up (line to space) is half a line gap higher. E4 is the bottom line."""
    svg = make_piece([note(pitch, octave)])
    staff = groups(svg, "staff")[0]
    lines = staff_lines(staff)
    half_gap = (lines[-1] - lines[0]) / 8
    steps_above_e4 = (octave * 7 + LETTERS.index(pitch)) - (4 * 7 + LETTERS.index("E"))

    assert notehead_y(groups(svg, "note")[0]) == pytest.approx(lines[-1] - steps_above_e4 * half_gap)


def test_higher_notes_are_drawn_higher(make_piece):
    svg = make_piece([note("C"), note("E"), note("G"), note("C", 5)])
    heights = [notehead_y(n) for n in groups(svg, "note")]

    assert heights == sorted(heights, reverse=True)   # smaller y is higher on the page


@pytest.mark.parametrize("duration", ["whole", "half", "quarter", "eighth", "16th"])
def test_note_head_matches_duration(make_piece, duration):
    svg = make_piece([note("G", 4, duration)])
    head = child_groups(groups(svg, "note")[0], "notehead")[0]
    assert glyphs(head) == [NOTEHEADS[duration]]


@pytest.mark.parametrize("duration, has_stem", [
    ("whole", False), ("half", True), ("quarter", True), ("eighth", True), ("16th", True),
])
def test_stem_matches_duration(make_piece, duration, has_stem):
    svg = make_piece([note("G", 4, duration)])
    assert bool(child_groups(groups(svg, "note")[0], "stem")) is has_stem


@pytest.mark.parametrize("pitch, octave", [("G", 4), ("D", 5)])   # stem up and stem down
@pytest.mark.parametrize("duration", ["whole", "half", "quarter", "eighth", "16th"])
def test_flag_matches_duration(make_piece, duration, pitch, octave):
    svg = make_piece([note(pitch, octave, duration)])
    flags = child_groups(groups(svg, "note")[0], "flag")

    if duration in FLAGS:
        assert len(flags) == 1
        assert set(glyphs(flags[0])) <= FLAGS[duration]
    else:
        assert flags == []


# --- Accidentals are shown ----------------------------------------------------

def drawn_accidentals(note_group):
    """Accidental signs actually drawn on a note.

    Verovio also adds an empty "accid" group when the key signature already
    supplies the sharp or flat; it draws nothing, so it is not counted.
    """
    return [g for accid in child_groups(note_group, "accid") for g in glyphs(accid)]


@pytest.mark.parametrize("accidental", ["sharp", "flat"])
def test_chosen_accidental_is_shown(make_piece, accidental):
    svg = make_piece([note("B", 4, "quarter", accidental)])
    assert drawn_accidentals(groups(svg, "note")[0]) == [ACCIDENTAL_GLYPHS[accidental]]


def test_plain_note_has_no_accidental(make_piece):
    svg = make_piece([note("B")])
    assert drawn_accidentals(groups(svg, "note")[0]) == []


def test_natural_with_nothing_to_cancel_is_not_drawn(make_piece):
    """Standard notation: B natural in C major needs no sign."""
    svg = make_piece([note("B", 4, "quarter", "natural")])
    assert drawn_accidentals(groups(svg, "note")[0]) == []


def test_key_signature_sharp_is_not_repeated_on_the_note(make_piece):
    """F in G major is F-sharp from the key signature, so no extra sign is drawn."""
    svg = make_piece([note("F")], key="G major")
    assert drawn_accidentals(groups(svg, "note")[0]) == []


def test_natural_against_the_key_signature_is_shown(make_piece):
    svg = make_piece([note("F", 4, "quarter", "natural")], key="G major")
    assert drawn_accidentals(groups(svg, "note")[0]) == [ACCIDENTAL_GLYPHS["natural"]]


def test_flat_against_a_sharp_key_is_shown(make_piece):
    svg = make_piece([note("F", 4, "quarter", "flat")], key="G major")
    assert drawn_accidentals(groups(svg, "note")[0]) == [ACCIDENTAL_GLYPHS["flat"]]


# --- Rests --------------------------------------------------------------------

@pytest.mark.parametrize("duration", ["whole", "half", "quarter", "eighth", "16th"])
def test_rest_symbol_matches_duration(make_piece, duration):
    svg = make_piece([rest(duration)])
    drawn = groups(svg, "rest") + groups(svg, "mRest")   # a whole-bar rest is drawn as mRest

    assert len(drawn) == 1
    assert glyphs(drawn[0]) == [RESTS[duration]]


def test_one_svg_rest_element_per_rest(make_piece):
    svg = make_piece([rest(), note("C"), rest("eighth"), rest("eighth")])

    assert notes_and_rests(svg).count("rest") == 3
    assert len(groups(svg, "note")) == 1


def test_notes_and_rests_are_drawn_in_order(make_piece):
    svg = make_piece([note("C"), rest("half"), note("E")])
    assert notes_and_rests(svg) == ["note", "rest", "note"]


# --- Key signature ------------------------------------------------------------

@pytest.mark.parametrize("key", [value for value, _ in KEY_SIGNATURES])
def test_key_signature_shows_the_right_sharps_or_flats(make_piece, key):
    svg = make_piece([note("C", 5)], key=key)
    expected = key_accidentals(key)
    drawn = [g for sig in groups(svg, "keySig") for a in child_groups(sig, "keyAccid") for g in glyphs(a)]

    assert len(drawn) == len(expected)
    assert set(drawn) == {ACCIDENTAL_GLYPHS[a] for a in expected.values()}


def test_c_major_has_no_key_signature_accidentals(make_piece):
    svg = make_piece([note("C")], key="C major")
    assert not any(child_groups(sig, "keyAccid") for sig in groups(svg, "keySig"))


# --- Time signature -----------------------------------------------------------

@pytest.mark.parametrize("time_signature", TIME_SIGNATURES)
def test_time_signature_shows_its_numbers(make_piece, time_signature):
    top, bottom = time_signature.split("/")
    svg = make_piece([note("C", 5)], time_signature=time_signature)

    meters = groups(svg, "meterSig")
    assert len(meters) == 1
    assert glyphs(meters[0]) == [digit(top), digit(bottom)]


# --- Bar lines ----------------------------------------------------------------

@pytest.mark.parametrize("time_signature, duration, count", [
    ("4/4", "quarter", 4),    # exactly one bar
    ("4/4", "quarter", 8),    # two full bars
    ("4/4", "quarter", 5),    # one full bar, one started
    ("3/4", "quarter", 6),
    ("2/4", "quarter", 5),
    ("6/8", "eighth", 6),
    ("6/8", "eighth", 7),
])
def test_bar_lines_appear_where_each_measure_fills_up(make_piece, time_signature, duration, count):
    top, bottom = (int(n) for n in time_signature.split("/"))
    beats_per_bar = top * 4 / bottom
    expected_bars = math.ceil(count * BEATS[duration] / beats_per_bar)

    svg = make_piece([note("C", 5, duration)] * count, time_signature=time_signature)

    assert len(groups(svg, "measure")) == expected_bars
    assert len(groups(svg, "barLine")) == expected_bars


def test_each_full_bar_holds_the_right_number_of_notes(make_piece):
    svg = make_piece([note("C", 5)] * 6, time_signature="3/4")
    per_bar = [len(child_groups(m, "note")) for m in groups(svg, "measure")]
    assert per_bar == [3, 3]


# --- The staff updates right after a note or rest is added --------------------

def test_staff_updates_after_each_note_or_rest(logged_in_client, test_user):
    piece = Composition(user_id=test_user.id, title="Live update", key_signature="C major",
                        time_signature="4/4", tempo=100)
    db.session.add(piece)
    db.session.commit()
    url = f"/compositions/{piece.id}/notes"

    logged_in_client.post(url, data={"pitch": "C", "octave": "4", "duration": "quarter", "accidental": ""})
    assert notes_and_rests(editor_svg(logged_in_client, piece.id)) == ["note"]

    logged_in_client.post(url, data={"is_rest": "1", "duration": "quarter"})
    assert notes_and_rests(editor_svg(logged_in_client, piece.id)) == ["note", "rest"]

    logged_in_client.post(url, data={"pitch": "E", "octave": "4", "duration": "quarter", "accidental": ""})
    assert notes_and_rests(editor_svg(logged_in_client, piece.id)) == ["note", "rest", "note"]
