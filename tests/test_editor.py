"""Tests for US-03-T3 (NTT-37): composition editor page shell."""
from types import SimpleNamespace

import pytest

from compositions import render_editor, sample_composition

PREVIEW_URL = "/compositions/preview"


@pytest.fixture
def html(client):
    response = client.get(PREVIEW_URL)
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_preview_page_loads(client):
    assert client.get(PREVIEW_URL).status_code == 200


def test_editor_uses_base_layout(html):
    assert "<nav" in html
    assert "/static/css/style.css" in html
    assert "<title>Ode to Joy (opening) · Noted!</title>" in html


def test_header_shows_composition_details(html):
    assert "Ode to Joy (opening)" in html
    assert "C major" in html
    assert "4/4" in html
    assert "= 100" in html


def test_page_has_staff_area_and_note_entry(html):
    assert 'id="staff-area"' in html
    assert 'class="note-form"' in html


def test_notes_listed_in_order(html):
    chips = html.split('class="note-list"')[1].split("</ol>")[0]
    order = [c.strip()[:2] for c in chips.split('<li class="note-chip">')[1:]]
    assert order == ["E4", "E4", "F4", "G4", "G4", "F4", "E4", "D4"]


@pytest.mark.parametrize("field, values", [
    ("pitch", ["C", "D", "E", "F", "G", "A", "B"]),
    ("octave", ["3", "4", "5", "6"]),
    ("duration", ["whole", "half", "quarter", "eighth"]),
    ("accidental", ["", "sharp", "flat"]),
])
def test_note_form_offers_every_option(html, field, values):
    for v in values:
        assert f'name="{field}"' in html
        assert f'value="{v}"' in html


def test_form_field_names_match_note_model(html):
    for field in ["pitch", "octave", "duration", "accidental", "is_rest"]:
        assert f'name="{field}"' in html


def test_sensible_defaults_are_selected(html):
    assert 'id="octave-4" value="4" checked' in html
    assert 'id="duration-quarter" value="quarter" checked' in html


def test_add_button_disabled_in_preview(html):
    assert "Preview with sample data" in html
    assert "disabled" in html.split("Add note</button>")[0].split("<button")[-1]


def test_empty_composition_shows_hint(app):
    empty = SimpleNamespace(**{**vars(sample_composition()), "notes": []})
    with app.test_request_context("/"):
        html = render_editor(empty)
    assert "No notes yet." in html
    assert 'class="note-list"' not in html
    assert "Preview with sample data" not in html


def test_rest_and_accidentals_render(app):
    comp = sample_composition()
    comp.notes = [
        SimpleNamespace(position=1, pitch="F", octave=4, duration="eighth", accidental="sharp", is_rest=False),
        SimpleNamespace(position=2, pitch="B", octave=4, duration="half", accidental="flat", is_rest=False),
        SimpleNamespace(position=3, pitch=None, octave=None, duration="quarter", accidental=None, is_rest=True),
    ]
    with app.test_request_context("/"):
        html = render_editor(comp)
    assert "F&#9839;4" in html
    assert "B&#9837;4" in html
    assert "Rest" in html
