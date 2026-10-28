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
