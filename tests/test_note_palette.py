"""Tests for US-04-T2 (NTT-40): note-entry palette in the composition editor."""
from types import SimpleNamespace

import pytest

from compositions import DURATIONS, RANGE_HIGH, RANGE_LOW, add_note_url, render_editor


def piece(composition_id=7):
    return SimpleNamespace(
        id=composition_id, title="Palette test", key_signature="C major",
        time_signature="4/4", tempo=100, notes=[],
    )


def render(app, composition, preview=False):
    with app.test_request_context("/"):
        return render_editor(composition, preview=preview)


def add_button(html):
    return html.split("Add note</button>")[0].split("<button")[-1]


def test_sixteenth_note_offered(app):
    # US-04 acceptance: whole, half, quarter, eighth, sixteenth.
    assert [d for d, _ in DURATIONS] == ["whole", "half", "quarter", "eighth", "16th"]
    html = render(app, piece())
    assert 'id="duration-16th" value="16th"' in html
    assert ">Sixteenth</label>" in html


def test_range_is_a3_to_c6(app):
    assert RANGE_LOW == ("A", 3)
    assert RANGE_HIGH == ("C", 6)
    html = render(app, piece())
    assert 'data-range-low="A3"' in html
    assert 'data-range-high="C6"' in html
    assert "Treble clef range: A3 to C6" in html


def test_palette_script_and_preview_present(app):
    html = render(app, piece())
    assert "js/note_palette.js" in html
    assert 'id="note-preview-text"' in html
    assert 'id="is-rest"' in html


def test_add_button_disabled_until_add_note_route_exists(app):
    html = render(app, piece())
    assert "disabled" in add_button(html)
    assert "NTT-41" in add_button(html)
    assert 'action=""' in html


def test_no_add_note_url_for_unsaved_piece(app):
    with app.test_request_context("/"):
        assert add_note_url(piece(composition_id=None)) is None


def test_palette_wires_up_once_add_note_route_exists(app):
    # Stand-in for Aaron's route (NTT-41): endpoint compositions.add_note,
    # POST /compositions/<id>/notes.
    app.add_url_rule(
        "/compositions/<int:composition_id>/notes",
        endpoint="compositions.add_note",
        view_func=lambda composition_id: "",
        methods=["POST"],
    )
    html = render(app, piece(composition_id=7))
    assert 'action="/compositions/7/notes"' in html
    assert "disabled" not in add_button(html)


def test_preview_page_never_enables_add(app):
    app.add_url_rule(
        "/compositions/<int:composition_id>/notes",
        endpoint="compositions.add_note",
        view_func=lambda composition_id: "",
        methods=["POST"],
    )
    html = render(app, piece(), preview=True)
    assert "disabled" in add_button(html)


# --- "Key" accidental: notes follow the key signature (decided Oct 28) -------

from compositions import ACCIDENTALS, effective_accidental, key_accidentals


@pytest.mark.parametrize("key, expected", [
    ("C major", {}),
    ("G major", {"F": "sharp"}),
    ("D major", {"F": "sharp", "C": "sharp"}),
    ("F major", {"B": "flat"}),
    ("Bb major", {"B": "flat", "E": "flat"}),
    ("C# major", {k: "sharp" for k in "FCGDAEB"}),
    ("Cb major", {k: "flat" for k in "BEADGCF"}),
    (None, {}),
])
def test_key_accidentals(key, expected):
    assert key_accidentals(key) == expected


def test_effective_accidental():
    assert effective_accidental("F", "", "G major") == "sharp"      # follows the key
    assert effective_accidental("F", "natural", "G major") == "natural"  # cancels it
    assert effective_accidental("G", "", "G major") == ""           # not in the key
    assert effective_accidental("F", "flat", "G major") == "flat"   # explicit wins


def test_palette_offers_key_button_as_default(app):
    assert [v for v, _, _ in ACCIDENTALS] == ["", "natural", "sharp", "flat"]
    html = render(app, piece())
    assert 'id="accidental-key" value="" checked' in html
    assert 'id="accidental-natural" value="natural"' in html


def test_palette_receives_key_signature(app):
    g_major = SimpleNamespace(**{**vars(piece()), "key_signature": "G major"})
    html = render(app, g_major)
    assert "data-key-accidentals='{\"F\": \"sharp\"}'" in html


def test_note_list_shows_sounding_accidental(app):
    notes = [
        SimpleNamespace(position=1, pitch="F", octave=4, duration="quarter", accidental="", is_rest=False),
        SimpleNamespace(position=2, pitch="F", octave=4, duration="quarter", accidental="natural", is_rest=False),
    ]
    g_major = SimpleNamespace(**{**vars(piece()), "key_signature": "G major", "notes": notes})
    chips = render(app, g_major).split('class="note-list"')[1].split("</ol>")[0]
    assert "F&#9839;4" in chips   # F follows the key: F-sharp
    assert "F&#9838;4" in chips   # explicit natural
