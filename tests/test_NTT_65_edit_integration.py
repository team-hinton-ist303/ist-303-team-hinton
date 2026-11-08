"""NTT-65: selection, palette, saving, and validation integration."""

from html.parser import HTMLParser
import xml.etree.ElementTree as ET

import pytest

from models import Composition, Note, db


class EditorHTML(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.inputs = []
        self.forms = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input":
            self.inputs.append(attrs)
        elif tag == "form":
            self.forms.append(attrs)

    def checked(self, name):
        return [
            item.get("value")
            for item in self.inputs
            if item.get("name") == name and "checked" in item
        ]


@pytest.fixture
def edit_piece(test_user):
    piece = Composition(
        user_id=test_user.id,
        title="Edit integration",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )
    db.session.add(piece)
    db.session.flush()
    for position, pitch, octave, duration, accidental in [
        (1, "C", 4, "quarter", ""),
        (2, "B", 4, "eighth", "flat"),
        (3, None, None, "half", None),
    ]:
        db.session.add(Note(
            composition_id=piece.id,
            position=position,
            pitch=pitch,
            octave=octave,
            duration=duration,
            accidental=accidental,
            is_rest=pitch is None,
        ))
    db.session.commit()
    return piece


def saved_notes(piece):
    db.session.expire_all()
    notes = db.session.execute(
        db.select(Note)
        .where(Note.composition_id == piece.id)
        .order_by(Note.position)
    ).scalars().all()
    return {
        n.id: (
            n.position, n.pitch, n.octave,
            n.duration, n.accidental, n.is_rest,
        )
        for n in notes
    }


def svg_note(html, note_id):
    import re

    start = html.index("<svg")
    depth = 0
    end = None
    for match in re.finditer(r"</?svg(?=[ >])[^>]*>", html[start:]):
        tag = match.group(0)
        if tag.startswith("</"):
            depth -= 1
        elif not tag.rstrip().endswith("/>"):
            depth += 1
        if depth == 0:
            end = start + match.end()
            break

    assert end is not None, "Outer SVG closing tag not found"
    root = ET.fromstring(html[start:end])
    return next(
        element for element in root.iter()
        if element.get("data-note-id") == str(note_id)
    )


def test_selecting_note_fills_palette_and_targets_update(
    logged_in_client, edit_piece
):
    selected = edit_piece.notes[1]
    before = saved_notes(edit_piece)

    response = logged_in_client.get(
        f"/compositions/{edit_piece.id}?note={selected.id}"
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    page = EditorHTML(html)

    assert page.checked("pitch") == ["B"]
    assert page.checked("octave") == ["4"]
    assert page.checked("duration") == ["eighth"]
    assert page.checked("accidental") == ["flat"]
    assert page.checked("is_rest") == []
    form = next(f for f in page.forms if f.get("id") == "note-form")
    assert form["method"].lower() == "post"
    assert form["action"] == (
        f"/compositions/{edit_piece.id}/notes/{selected.id}"
    )
    assert "Save changes" in html
    assert saved_notes(edit_piece) == before


def test_selecting_rest_fills_rest_palette(logged_in_client, edit_piece):
    rest = edit_piece.notes[2]
    response = logged_in_client.get(
        f"/compositions/{edit_piece.id}?note={rest.id}"
    )
    assert response.status_code == 200
    page = EditorHTML(response.get_data(as_text=True))
    assert page.checked("is_rest") == ["1"]
    assert page.checked("duration") == ["half"]


def test_save_changes_only_selected_note_and_renders_updated_staff(
    logged_in_client, edit_piece
):
    selected = edit_piece.notes[1]
    selected_id = selected.id
    before = saved_notes(edit_piece)

    initial = logged_in_client.get(
        f"/compositions/{edit_piece.id}?note={selected_id}"
    )
    assert initial.status_code == 200
    old_svg_note = ET.tostring(
        svg_note(initial.get_data(as_text=True), selected_id)
    )

    response = logged_in_client.post(
        f"/compositions/{edit_piece.id}/notes/{selected_id}",
        data={
            "pitch": "E",
            "octave": "5",
            "duration": "half",
            "accidental": "natural",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"] == f"/compositions/{edit_piece.id}"

    after = saved_notes(edit_piece)
    assert set(after) == set(before)
    assert after[selected_id] == (2, "E", 5, "half", "natural", False)
    assert {
        key: value for key, value in after.items() if key != selected_id
    } == {
        key: value for key, value in before.items() if key != selected_id
    }

    page = logged_in_client.get(response.headers["Location"])
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert "Note updated" in html
    assert ET.tostring(svg_note(html, selected_id)) != old_svg_note

    reopened = logged_in_client.get(
        f"/compositions/{edit_piece.id}?note={selected_id}"
    )
    palette = EditorHTML(reopened.get_data(as_text=True))
    assert palette.checked("pitch") == ["E"]
    assert palette.checked("octave") == ["5"]
    assert palette.checked("duration") == ["half"]
    assert palette.checked("accidental") == ["natural"]


@pytest.mark.parametrize("changes, message", [
    ({"pitch": ""}, "Choose a pitch"),
    ({"pitch": "H"}, "Choose a pitch"),
    ({"octave": "bad"}, "Choose an octave"),
    ({"accidental": "unknown"}, "Choose a valid accidental"),
    ({"duration": "invalid"}, "Choose a valid note duration"),
    ({"pitch": "A", "octave": "3", "accidental": "flat"}, "below"),
    ({"pitch": "C", "octave": "6", "accidental": "sharp"}, "above"),
])
def test_invalid_edit_shows_error_and_preserves_all_notes(
    logged_in_client, edit_piece, changes, message
):
    selected_id = edit_piece.notes[1].id
    before = saved_notes(edit_piece)
    data = {
        "pitch": "D",
        "octave": "4",
        "duration": "quarter",
        "accidental": "",
        **changes,
    }

    response = logged_in_client.post(
        f"/compositions/{edit_piece.id}/notes/{selected_id}",
        data=data,
    )

    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Edit integration" in html
    assert message in html
    assert saved_notes(edit_piece) == before
