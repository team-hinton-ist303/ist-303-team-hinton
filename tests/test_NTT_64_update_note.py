
"""NTT-64: Tests for updating an existing note."""

import pytest
from werkzeug.security import generate_password_hash

from models import db, User, Composition, Note


@pytest.fixture
def note_data(client):
    owner = User(
        username="update_owner",
        email="update_owner@example.com",
        password_hash=generate_password_hash("test123"),
    )
    other = User(
        username="update_other",
        email="update_other@example.com",
        password_hash=generate_password_hash("test123"),
    )
    db.session.add_all([owner, other])
    db.session.flush()

    piece = Composition(
        user_id=owner.id,
        title="My Test Music",
        key_signature="G major",
        time_signature="4/4",
        tempo=100,
    )
    other_piece = Composition(
        user_id=other.id,
        title="Other Music",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )
    db.session.add_all([piece, other_piece])
    db.session.flush()

    note = Note(
        composition_id=piece.id,
        position=1,
        pitch="F",
        octave=4,
        duration="quarter",
        accidental="sharp",
        is_rest=False,
    )
    db.session.add(note)
    db.session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "update_owner", "password": "test123"},
    )
    assert response.status_code == 302

    return piece.id, note.id, other_piece.id


def test_update_note_and_key_accidental(client, note_data):
    piece_id, note_id, _ = note_data

    response = client.post(
        f"/compositions/{piece_id}/notes/{note_id}",
        data={
            "pitch": "F",
            "octave": "4",
            "duration": "half",
            "accidental": "",
        },
    )

    assert response.status_code == 302

    note = db.session.get(Note, note_id)
    assert note.pitch == "F"
    assert note.octave == 4
    assert note.duration == "half"
    assert note.accidental == ""
    assert note.position == 1

    page = client.get(response.headers["Location"])
    assert "Note updated" in page.get_data(as_text=True)


@pytest.mark.parametrize("bad_data", [
    {
        "pitch": "C",
        "octave": "6",
        "duration": "quarter",
        "accidental": "sharp",
    },
    {
        "pitch": "F",
        "octave": "4",
        "duration": "invalid",
        "accidental": "",
    },
])
def test_invalid_update_returns_400(client, note_data, bad_data):
    piece_id, note_id, _ = note_data

    response = client.post(
        f"/compositions/{piece_id}/notes/{note_id}",
        data=bad_data,
    )

    assert response.status_code == 400

    note = db.session.get(Note, note_id)
    assert note.pitch == "F"
    assert note.duration == "quarter"
    assert note.accidental == "sharp"


def test_other_users_composition_returns_404(client, note_data):
    piece_id, note_id, other_piece_id = note_data

    response = client.post(
        f"/compositions/{other_piece_id}/notes/{note_id}",
        data={
            "pitch": "C",
            "octave": "4",
            "duration": "quarter",
            "accidental": "",
        },
    )

    assert response.status_code == 404


def test_update_note_to_rest(client, note_data):
    piece_id, note_id, _ = note_data

    response = client.post(
        f"/compositions/{piece_id}/notes/{note_id}",
        data={
            "is_rest": "1",
            "duration": "half",
        },
    )

    assert response.status_code == 302

    note = db.session.get(Note, note_id)
    assert note.is_rest is True
    assert note.pitch is None
    assert note.octave is None
    assert note.duration == "half"
    assert note.position == 1
