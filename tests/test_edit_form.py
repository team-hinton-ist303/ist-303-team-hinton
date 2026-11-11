"""Tests for US-07-T2 (NTT-63): the palette fills in with the selected note's values.

Selecting a note (NTT-62, ?note=<id>) turns the palette into an edit form.
It saves to the update route from the edit contract (NTT-64):
POST /compositions/<id>/notes/<note_id>, endpoint compositions.update_note.
"""
import re

import pytest

import compositions
from compositions import palette_values
from models import Composition, Note, db


def make_piece(owner, key="C major", notes=()):
    """notes: (pitch, octave, duration, accidental) tuples; pitch None is a rest."""
    piece = Composition(user_id=owner.id, title="Edit form test", key_signature=key,
                        time_signature="4/4", tempo=100)
    db.session.add(piece)
    db.session.flush()
    for position, (pitch, octave, duration, accidental) in enumerate(notes, start=1):
        db.session.add(Note(composition_id=piece.id, position=position, duration=duration,
                            pitch=pitch, octave=octave, accidental=accidental,
                            is_rest=pitch is None))
    db.session.commit()
    return piece


def note_at(piece, position):
    return next(n for n in piece.notes if n.position == position)


def editor(client, piece, note=None):
    query = f"?note={note.id}" if note else ""
    response = client.get(f"/compositions/{piece.id}{query}")
    assert response.status_code == 200
    return response.get_data(as_text=True)


def checked(html, name):
    """Value of the checked radio in a palette group."""
    match = re.search(rf'name="{name}" id="[^"]+" value="([^"]*)" checked', html)
    return match.group(1) if match else None


def form_tag(html):
    return re.search(r'<form class="note-form"[^>]*>', html, re.S).group(0)


def submit_button(html):
    return html.split('class="note-form-actions"', 1)[1].split("</button>", 1)[0]


@pytest.fixture
def piece(test_user):
    return make_piece(test_user, notes=[
        ("E", 5, "half", None),
        ("B", 4, "eighth", "flat"),
        (None, None, "whole", None),
        ("A", 3, "16th", "natural"),
    ])


# --- Pre-filled with the note's values ------------------------------------------

def test_palette_fills_with_the_selected_note(logged_in_client, piece):
    html = editor(logged_in_client, piece, note_at(piece, 1))
    assert (checked(html, "pitch"), checked(html, "octave"), checked(html, "duration")) == ("E", "5", "half")
    assert checked(html, "accidental") == ""


def test_explicit_accidentals_are_filled_in(logged_in_client, piece):
    assert checked(editor(logged_in_client, piece, note_at(piece, 2)), "accidental") == "flat"
    assert checked(editor(logged_in_client, piece, note_at(piece, 4)), "accidental") == "natural"


def test_lowest_and_shortest_values_are_filled_in(logged_in_client, piece):
    html = editor(logged_in_client, piece, note_at(piece, 4))
    assert (checked(html, "pitch"), checked(html, "octave"), checked(html, "duration")) == ("A", "3", "16th")


def test_rest_fills_rest_box_and_duration(logged_in_client, piece):
    html = editor(logged_in_client, piece, note_at(piece, 3))
    assert re.search(r'id="is-rest" value="1" checked', html)
    assert checked(html, "duration") == "whole"


def test_explicit_sharp_in_key_stays_sharp(logged_in_client, test_user):
    """F saved as "sharp" in G major was an explicit ♯ choice, so the form shows ♯, not Key."""
    g_major = make_piece(test_user, key="G major", notes=[("F", 4, "quarter", "sharp")])
    assert checked(editor(logged_in_client, g_major, g_major.notes[0]), "accidental") == "sharp"


def test_key_accidental_stored_as_blank_also_shows_as_key(logged_in_client, test_user):
    g_major = make_piece(test_user, key="G major", notes=[("F", 4, "quarter", "")])
    assert checked(editor(logged_in_client, g_major, g_major.notes[0]), "accidental") == ""


def test_natural_against_the_key_stays_natural(logged_in_client, test_user):
    g_major = make_piece(test_user, key="G major", notes=[("F", 4, "quarter", "natural")])
    assert checked(editor(logged_in_client, g_major, g_major.notes[0]), "accidental") == "natural"


@pytest.mark.parametrize("name", ["pitch", "octave", "duration", "accidental"])
def test_exactly_one_choice_checked_per_group(logged_in_client, piece, name):
    html = editor(logged_in_client, piece, note_at(piece, 2))
    assert len(re.findall(rf'name="{name}" id="[^"]+" value="[^"]*" checked', html)) == 1


# --- Edit mode vs add mode -------------------------------------------------------

def test_edit_mode_has_title_save_and_cancel(logged_in_client, piece):
    html = editor(logged_in_client, piece, note_at(piece, 2))
    assert "Edit note 2" in html
    assert "Save changes" in submit_button(html)
    assert "Add note</button>" not in html
    assert f'<a class="btn" href="/compositions/{piece.id}">Cancel</a>' in html
    assert "Change to:" in html


def test_without_selection_palette_is_unchanged(logged_in_client, piece):
    html = editor(logged_in_client, piece)
    assert (checked(html, "pitch"), checked(html, "octave"), checked(html, "duration"),
            checked(html, "accidental")) == ("C", "4", "quarter", "")
    assert "Edit note" not in html
    assert f'action="/compositions/{piece.id}/notes"' in form_tag(html)
    assert "Add note</button>" in html
    assert "Next:" in html


def test_save_is_disabled_when_the_update_route_is_missing(logged_in_client, piece, monkeypatch):
    """Before NTT-64 merges there is no update route; simulate that either way."""
    monkeypatch.setattr(compositions, "update_note_url", lambda composition, note: None)
    html = editor(logged_in_client, piece, note_at(piece, 1))
    assert 'action=""' in form_tag(html)
    assert "disabled" in submit_button(html)
    assert "update route (NTT-64)" in submit_button(html)


def test_form_posts_to_the_update_route(app, client, test_user):
    """Uses NTT-64's route once it's merged; until then, a stand-in at the contract's URL."""
    if "compositions.update_note" not in app.view_functions:
        app.add_url_rule("/compositions/<int:composition_id>/notes/<int:note_id>",
                         endpoint="compositions.update_note", view_func=lambda **_: "", methods=["POST"])
    client.post("/auth/login", data={"username": "tester", "password": "test-password"})
    piece = make_piece(test_user, notes=[("C", 4, "quarter", None)])
    note = piece.notes[0]

    html = editor(client, piece, note)
    assert f'action="/compositions/{piece.id}/notes/{note.id}"' in form_tag(html)
    assert "disabled" not in submit_button(html)


# --- palette_values on its own ---------------------------------------------------

def test_palette_values_defaults_with_no_selection():
    assert palette_values(None, "C major") == {
        "pitch": "C", "octave": 4, "duration": "quarter", "accidental": "", "is_rest": False}
