"""Tests for US-08-T3 (NTT-68): deleting a note.

Acceptance criteria covered (from story US-08, NTT-10):
  - Deleting a note removes it and the remaining notes keep their order.
  - The staff redraws without the note.

Uses the full flow a user takes: add notes through the add-note route, select one
in the editor, press Delete (NTT-66), which posts to the delete route (NTT-67),
then read the editor page and its sheet music SVG again.

test_NTT_67_delete_note.py already covers position renumbering and other users'
notes at the route level; these tests add the editor, the staff, rests, and the
delete-then-add flow.

Every rendered note and rest carries data-note-id (NTT-53), so the staff can be
checked for exactly which notes are still drawn. Notes are kept inside one bar
each so music21 does not split them into tied pieces.
"""
import html as html_lib
import re
import xml.etree.ElementTree as ET

import pytest

from models import Composition, Note, db

SVG_NS = "{http://www.w3.org/2000/svg}"
C_D_E_REST_G = [
    ("C", 4, "quarter", ""),
    ("D", 4, "quarter", "sharp"),
    ("E", 4, "eighth", ""),
    (None, None, "eighth", ""),     # rest
    ("G", 4, "quarter", "flat"),   # 1 + 1 + .5 + .5 + 1 = one full 4/4 bar
]


# --- Helpers ------------------------------------------------------------------

@pytest.fixture
def make_piece(logged_in_client, test_user):
    """A piece owned by the logged-in user, with notes added through the real route."""
    def build(notes=C_D_E_REST_G, time_signature="4/4"):
        piece = Composition(user_id=test_user.id, title="Delete test", key_signature="C major",
                            time_signature=time_signature, tempo=100)
        db.session.add(piece)
        db.session.commit()
        for pitch, octave, duration, accidental in notes:
            add(logged_in_client, piece.id, pitch, octave, duration, accidental)
        return piece.id
    return build


def add(client, piece_id, pitch, octave=4, duration="quarter", accidental=""):
    data = ({"is_rest": "1", "duration": duration} if pitch is None else
            {"pitch": pitch, "octave": str(octave), "duration": duration, "accidental": accidental})
    response = client.post(f"/compositions/{piece_id}/notes", data=data)
    assert response.status_code == 302


def delete(client, piece_id, note_id):
    return client.post(f"/compositions/{piece_id}/notes/{note_id}/delete")


def saved(piece_id):
    """(position, pitch, octave, duration, accidental, is_rest) for each saved note, in order."""
    db.session.expire_all()
    notes = db.session.execute(
        db.select(Note).where(Note.composition_id == piece_id).order_by(Note.position)
    ).scalars().all()
    return [(n.id, n.position, n.pitch, n.octave, n.duration, n.accidental, n.is_rest) for n in notes]


def ids(piece_id):
    return [row[0] for row in saved(piece_id)]


def content(piece_id):
    """Each note without its id or position, to check nothing else changed."""
    return [row[2:] for row in saved(piece_id)]


def editor_html(client, piece_id, **query):
    return client.get(f"/compositions/{piece_id}", query_string=query).get_data(as_text=True)


def staff_svg(html):
    match = re.search(r'<div class="staff-svg[^"]*">\s*(<svg.*</svg>)\s*</div>', html, re.S)
    assert match, "the editor page has no sheet music SVG"
    return match.group(1)


def drawn(html):
    """('note' or 'rest', note id) for each note and rest drawn on the staff, in order."""
    root = ET.fromstring(staff_svg(html))
    out = []
    for element in root.iter(SVG_NS + "g"):
        kind = set((element.get("class") or "").split()) & {"note", "rest", "mRest"}
        if kind:
            out.append(("note" if "note" in kind else "rest", int(element.get("data-note-id"))))
    return out


def drawn_ids(html):
    return [note_id for _, note_id in drawn(html)]


def bar_count(html):
    root = ET.fromstring(staff_svg(html))
    return sum("measure" in (e.get("class") or "").split() for e in root.iter(SVG_NS + "g"))


# --- The delete control (NTT-66) ----------------------------------------------

def test_no_delete_button_until_a_note_is_selected(logged_in_client, make_piece):
    piece_id = make_piece()
    assert 'id="delete-note-form"' not in editor_html(logged_in_client, piece_id)


@pytest.mark.parametrize("index", [0, 3])   # a note and a rest
def test_selected_note_shows_delete_button_for_that_note(logged_in_client, make_piece, index):
    piece_id = make_piece()
    note_id = ids(piece_id)[index]

    html = editor_html(logged_in_client, piece_id, note=note_id)

    assert f'action="/compositions/{piece_id}/notes/{note_id}/delete"' in html
    assert f'aria-label="Delete note {index + 1}"' in html
    assert "confirm(" in html                     # asks before deleting


# --- Deleting removes the note; the rest keep their order ---------------------

@pytest.mark.parametrize("index", [0, 1, 2, 3, 4])
def test_delete_removes_only_that_note_and_keeps_order(logged_in_client, make_piece, index):
    piece_id = make_piece()
    before = saved(piece_id)
    note_id = before[index][0]

    response = delete(logged_in_client, piece_id, note_id)

    after = saved(piece_id)
    assert response.status_code == 302
    assert [row[0] for row in after] == [row[0] for row in before if row[0] != note_id]
    assert [row[1] for row in after] == [1, 2, 3, 4]
    assert [row[2:] for row in after] == [row[2:] for row in before if row[0] != note_id]


def test_deleting_a_rest_keeps_the_notes_around_it(logged_in_client, make_piece):
    piece_id = make_piece()
    rest_id = ids(piece_id)[3]

    delete(logged_in_client, piece_id, rest_id)

    assert [row[2] for row in saved(piece_id)] == ["C", "D", "E", "G"]
    assert not any(row[6] for row in saved(piece_id))


def test_delete_notes_one_by_one_until_empty(logged_in_client, make_piece):
    piece_id = make_piece()

    for remaining in [4, 3, 2, 1, 0]:
        delete(logged_in_client, piece_id, ids(piece_id)[0])
        assert [row[1] for row in saved(piece_id)] == list(range(1, remaining + 1))


def test_note_added_after_a_delete_goes_at_the_end(logged_in_client, make_piece):
    piece_id = make_piece()
    delete(logged_in_client, piece_id, ids(piece_id)[1])

    add(logged_in_client, piece_id, "B", 4)

    rows = saved(piece_id)
    assert [row[1] for row in rows] == [1, 2, 3, 4, 5]
    assert rows[-1][2:4] == ("B", 4)


def test_delete_returns_to_editor_with_nothing_selected(logged_in_client, make_piece):
    piece_id = make_piece()

    response = delete(logged_in_client, piece_id, ids(piece_id)[0])

    assert response.headers["Location"] == f"/compositions/{piece_id}"


def test_editor_confirms_delete_and_lists_the_rest_in_order(logged_in_client, make_piece):
    piece_id = make_piece()
    delete(logged_in_client, piece_id, ids(piece_id)[1])       # D#4

    response = logged_in_client.get(f"/compositions/{piece_id}")
    html = response.get_data(as_text=True)
    note_list = html.split('class="note-list"', 1)[1].split("</ol>", 1)[0]
    labels = [html_lib.unescape(label).strip()
              for label in re.findall(r'class="note-chip-link"[^>]*>\s*([^<]+?)\s*<span', note_list)]

    assert "Note deleted" in html
    assert labels == ["C4", "E4", "Rest", "G♭4"]


# --- The staff redraws without the note ---------------------------------------

@pytest.mark.parametrize("index", [0, 1, 2, 3, 4])
def test_staff_redraws_without_the_deleted_note(logged_in_client, make_piece, index):
    piece_id = make_piece()
    before = ids(piece_id)
    assert drawn_ids(editor_html(logged_in_client, piece_id)) == before

    delete(logged_in_client, piece_id, before[index])

    html = editor_html(logged_in_client, piece_id)
    assert before[index] not in drawn_ids(html)
    assert drawn_ids(html) == [note_id for note_id in before if note_id != before[index]]


def test_staff_has_one_fewer_note_after_delete(logged_in_client, make_piece):
    piece_id = make_piece()
    delete(logged_in_client, piece_id, ids(piece_id)[0])

    kinds = [kind for kind, _ in drawn(editor_html(logged_in_client, piece_id))]
    assert kinds == ["note", "note", "rest", "note"]


def test_staff_redraws_without_a_deleted_rest(logged_in_client, make_piece):
    piece_id = make_piece()
    delete(logged_in_client, piece_id, ids(piece_id)[3])

    kinds = [kind for kind, _ in drawn(editor_html(logged_in_client, piece_id))]
    assert kinds == ["note", "note", "note", "note"]


def test_deleting_the_last_note_shows_the_empty_staff(logged_in_client, make_piece):
    piece_id = make_piece([("C", 4, "quarter", "")])
    delete(logged_in_client, piece_id, ids(piece_id)[0])

    html = editor_html(logged_in_client, piece_id)

    assert 'class="staff-svg staff-svg-empty"' in html
    assert drawn(html) == []


def test_bar_lines_redraw_after_delete(logged_in_client, make_piece):
    """Five quarters in 4/4 need two bars; after one is deleted they fit in one."""
    piece_id = make_piece([("C", 5, "quarter", "")] * 5)
    assert bar_count(editor_html(logged_in_client, piece_id)) == 2

    delete(logged_in_client, piece_id, ids(piece_id)[0])

    assert bar_count(editor_html(logged_in_client, piece_id)) == 1


# --- Safety -------------------------------------------------------------------

def test_delete_only_works_by_post(logged_in_client, make_piece):
    piece_id = make_piece()
    note_id = ids(piece_id)[0]

    response = logged_in_client.get(f"/compositions/{piece_id}/notes/{note_id}/delete")

    assert response.status_code == 405
    assert note_id in ids(piece_id)


def test_deleting_the_same_note_twice_changes_nothing_more(logged_in_client, make_piece):
    piece_id = make_piece()
    note_id = ids(piece_id)[0]
    delete(logged_in_client, piece_id, note_id)
    after_first = saved(piece_id)

    response = delete(logged_in_client, piece_id, note_id)

    assert response.status_code == 404
    assert saved(piece_id) == after_first


def test_logged_out_user_cannot_delete(client, logged_in_client, make_piece):
    piece_id = make_piece()
    note_id = ids(piece_id)[0]
    logged_in_client.post("/auth/logout")

    response = delete(client, piece_id, note_id)

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
    assert note_id in ids(piece_id)
