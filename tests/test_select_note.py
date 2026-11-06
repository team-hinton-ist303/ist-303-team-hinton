"""Tests for US-07-T1 (NTT-62): selecting a note in the editor with ?note=<id>.

The edit contract (NTT-62 to NTT-65): a note is selected with
GET /compositions/<id>?note=<note_id>. The edit form (NTT-63) and the
update route (NTT-64) build on this.
"""
import re

import pytest
from werkzeug.security import generate_password_hash

from models import Composition, Note, User, db


def make_piece(owner, notes=("C", "E", None, "G")):
    """A piece with notes; None in `notes` is a rest."""
    piece = Composition(user_id=owner.id, title="Select test", key_signature="C major",
                        time_signature="4/4", tempo=100)
    db.session.add(piece)
    db.session.flush()
    for position, pitch in enumerate(notes, start=1):
        db.session.add(Note(composition_id=piece.id, position=position, duration="quarter",
                            pitch=pitch, octave=None if pitch is None else 4,
                            accidental=None, is_rest=pitch is None))
    db.session.commit()
    return piece


@pytest.fixture
def piece(test_user):
    return make_piece(test_user)


def note_at(piece, position):
    return next(n for n in piece.notes if n.position == position)


def editor_html(client, piece, query=""):
    response = client.get(f"/compositions/{piece.id}{query}")
    assert response.status_code == 200
    return response.get_data(as_text=True)


def note_list(html):
    return html.split('class="note-list"', 1)[1].split("</ol>", 1)[0]


def selected_chips(html):
    return re.findall(r'<li class="note-chip is-selected">', note_list(html))


# --- Each note can be selected ---------------------------------------------------

def test_every_note_in_the_list_links_to_its_selection(logged_in_client, piece):
    html = editor_html(logged_in_client, piece)
    for note in piece.notes:
        assert f'href="/compositions/{piece.id}?note={note.id}"' in note_list(html)


def test_rests_can_be_selected_too(logged_in_client, piece):
    rest = note_at(piece, 3)
    html = editor_html(logged_in_client, piece, f"?note={rest.id}")
    assert len(selected_chips(html)) == 1
    assert "Selected: note 3." in html


def test_no_note_is_selected_by_default(logged_in_client, piece):
    html = editor_html(logged_in_client, piece)
    assert selected_chips(html) == []
    assert 'aria-current="true"' not in html
    assert "Click a note to select it." in html
    assert "data-selected-note" not in html


# --- Selecting with ?note=<id> ---------------------------------------------------

def test_selected_note_is_highlighted_in_the_list(logged_in_client, piece):
    note = note_at(piece, 2)
    html = editor_html(logged_in_client, piece, f"?note={note.id}")

    assert len(selected_chips(html)) == 1
    chip = note_list(html).split('<li class="note-chip is-selected">', 1)[1].split("</li>", 1)[0]
    assert "E4" in chip
    assert 'aria-current="true"' in chip


def test_selected_note_shows_its_position_and_a_way_to_clear(logged_in_client, piece):
    note = note_at(piece, 2)
    html = editor_html(logged_in_client, piece, f"?note={note.id}")

    assert "Selected: note 2." in html
    assert f'<a href="/compositions/{piece.id}">Clear selection</a>' in html


def test_staff_area_knows_the_selected_note_for_highlighting(logged_in_client, piece):
    note = note_at(piece, 4)
    html = editor_html(logged_in_client, piece, f"?note={note.id}")

    assert f'data-selected-note="{note.id}"' in html
    assert f'data-select-url="/compositions/{piece.id}"' in html
    assert "js/note_select.js" in html


def test_selecting_does_not_change_the_notes(logged_in_client, piece):
    before = [(n.position, n.pitch) for n in piece.notes]
    editor_html(logged_in_client, piece, f"?note={note_at(piece, 1).id}")
    db.session.expire_all()
    after = [(n.position, n.pitch) for n in db.session.get(Composition, piece.id).notes]
    assert after == before


# --- Bad or foreign ids are ignored ------------------------------------------------

@pytest.mark.parametrize("query", ["?note=", "?note=abc", "?note=99999", "?note=-1", "?note=1.5"])
def test_bad_note_id_shows_editor_with_nothing_selected(logged_in_client, piece, query):
    html = editor_html(logged_in_client, piece, query)
    assert selected_chips(html) == []
    assert "Selected:" not in html


def test_note_from_another_piece_cannot_be_selected(logged_in_client, piece, test_user):
    other_piece = make_piece(test_user, notes=("A",))
    foreign = other_piece.notes[0]

    html = editor_html(logged_in_client, piece, f"?note={foreign.id}")
    assert selected_chips(html) == []
    assert "Selected:" not in html


def test_other_users_piece_is_still_404_with_a_note_id(logged_in_client):
    stranger = User(username="stranger", email="stranger@example.com",
                    password_hash=generate_password_hash("x-password"))
    db.session.add(stranger)
    db.session.flush()
    theirs = make_piece(stranger)

    response = logged_in_client.get(f"/compositions/{theirs.id}?note={theirs.notes[0].id}")
    assert response.status_code == 404


def test_empty_piece_ignores_note_id(logged_in_client, test_user):
    empty = make_piece(test_user, notes=())
    html = editor_html(logged_in_client, empty, "?note=1")
    assert "No notes yet." in html
    assert "Selected:" not in html


def test_preview_page_has_no_selection_links(logged_in_client):
    html = logged_in_client.get("/compositions/preview").get_data(as_text=True)
    assert "?note=" not in note_list(html)
    assert "data-select-url" not in html
