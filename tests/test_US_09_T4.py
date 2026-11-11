"""US-09-T4: composition settings integration.

Deletion and access-control coverage also lives in
test_NTT_70_delete_piece.py and test_US_12_T3.py.
"""

from html.parser import HTMLParser

import pytest

import compositions
from models import Composition, Note, db


UPDATED = {
    "title": "Revised piece",
    "key_signature": "G major",
    "time_signature": "3/4",
    "tempo": "132",
}


@pytest.fixture
def settings_piece(test_user):
    piece = Composition(
        user_id=test_user.id,
        title="Original settings",
        key_signature="Bb major",
        time_signature="6/8",
        tempo=96,
    )
    db.session.add(piece)
    db.session.flush()
    db.session.add(Note(
        composition_id=piece.id,
        position=1,
        pitch="C",
        octave=4,
        duration="quarter",
        accidental="natural",
        is_rest=False,
    ))
    db.session.commit()
    return piece


def snapshot(piece_id):
    db.session.expire_all()
    piece = db.session.get(Composition, piece_id)
    return (
        piece.title, piece.key_signature, piece.time_signature,
        piece.tempo, piece.user_id, piece.updated_at,
        [
            (
                n.id, n.position, n.pitch, n.octave,
                n.duration, n.accidental, n.is_rest,
            )
            for n in piece.notes
        ],
    )


class SettingsHTML(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.inputs = {}
        self.selected_keys = []
        self.checked_times = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input":
            name = attrs.get("name")
            if name in ("title", "tempo"):
                self.inputs[name] = attrs.get("value")
            if name == "time_signature" and "checked" in attrs:
                self.checked_times.append(attrs.get("value"))
        if tag == "option" and "selected" in attrs:
            self.selected_keys.append(attrs.get("value"))


def test_all_settings_are_prefilled_without_changing_data(
    logged_in_client, settings_piece
):
    piece_id = settings_piece.id
    before = snapshot(piece_id)

    response = logged_in_client.get(f"/compositions/{piece_id}/settings")

    assert response.status_code == 200
    page = SettingsHTML(response.get_data(as_text=True))
    assert page.inputs == {"title": "Original settings", "tempo": "96"}
    assert page.selected_keys == ["Bb major"]
    assert page.checked_times == ["6/8"]
    assert snapshot(piece_id) == before


def test_updates_all_settings_redirects_and_preserves_notes(
    logged_in_client, settings_piece
):
    piece_id = settings_piece.id
    before = snapshot(piece_id)

    response = logged_in_client.post(
        f"/compositions/{piece_id}/settings", data=UPDATED
    )

    assert response.status_code == 302
    assert response.headers["Location"] == f"/compositions/{piece_id}"
    after = snapshot(piece_id)
    assert after[:4] == ("Revised piece", "G major", "3/4", 132)
    assert after[4] == before[4]
    assert after[6] == before[6]

    page = logged_in_client.get(response.headers["Location"])
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    header = html.split('class="editor-header"', 1)[1].split("</header>", 1)[0]
    for value in ("Revised piece", "G major", "3/4", "= 132"):
        assert value in header
    assert "Piece updated" in html


@pytest.mark.parametrize("has_notes", [True, False])
def test_redirected_editor_renders_staff_using_updated_settings(
    logged_in_client, settings_piece, monkeypatch, has_notes
):
    piece_id = settings_piece.id
    if not has_notes:
        for note in list(settings_piece.notes):
            db.session.delete(note)
        db.session.commit()
        db.session.expire_all()

    # Spy on the real renderer: record its input and still generate real SVG.
    name = "composition_to_svg" if has_notes else "empty_staff_svg"
    original = getattr(compositions, name)
    calls = []
    rendered = []

    def record_render(piece):
        calls.append((
            piece.id, piece.title, piece.key_signature,
            piece.time_signature, piece.tempo,
        ))
        svg = original(piece)
        rendered.append(svg)
        return svg

    monkeypatch.setattr(compositions, name, record_render)

    response = logged_in_client.post(
        f"/compositions/{piece_id}/settings", data=UPDATED
    )
    assert response.status_code == 302
    page = logged_in_client.get(response.headers["Location"])

    assert page.status_code == 200
    assert calls == [
        (piece_id, "Revised piece", "G major", "3/4", 132)
    ]
    assert len(rendered) == 1
    assert "<svg" in rendered[0]
    assert rendered[0] in page.get_data(as_text=True)


@pytest.mark.parametrize("changes, message", [
    ({"title": ""}, "Please give your piece a title."),
    ({"title": "   "}, "Please give your piece a title."),
    ({"tempo": "39"}, "Tempo must be between"),
    ({"tempo": "241"}, "Tempo must be between"),
    ({"tempo": "fast"}, "Tempo must be a whole number"),
    ({"key_signature": "invalid"}, "Please choose a key."),
    ({"time_signature": "invalid"}, "Please choose a time signature."),
])
def test_invalid_settings_preserve_entire_piece_and_notes(
    logged_in_client, settings_piece, changes, message
):
    piece_id = settings_piece.id
    before = snapshot(piece_id)

    response = logged_in_client.post(
        f"/compositions/{piece_id}/settings",
        data={**UPDATED, **changes},
    )

    assert response.status_code == 400
    assert message in response.get_data(as_text=True)
    assert snapshot(piece_id) == before
