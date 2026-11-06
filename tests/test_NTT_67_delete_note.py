
"""NTT-67: Test deleting notes and renumbering positions."""

import pytest
from werkzeug.security import generate_password_hash
from models import db, User, Composition, Note


@pytest.fixture
def note_data(client):
    owner = User(
        username="delete_owner",
        email="delete_owner@example.com",
        password_hash=generate_password_hash("test123"),
    )
    other = User(
        username="delete_other",
        email="delete_other@example.com",
        password_hash=generate_password_hash("test123"),
    )

    db.session.add_all([owner, other])
    db.session.flush()

    piece = Composition(
        user_id=owner.id,
        title="Delete Test",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )
    other_piece = Composition(
        user_id=other.id,
        title="Other Piece",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )

    db.session.add_all([piece, other_piece])
    db.session.flush()

    notes = []
    for pos, pitch in enumerate(["C", "D", "E"], start=1):
        note = Note(
            composition_id=piece.id,
            position=pos,
            pitch=pitch,
            octave=4,
            duration="quarter",
            is_rest=False,
        )
        db.session.add(note)
        notes.append(note)

    other_note = Note(
        composition_id=other_piece.id,
        position=1,
        pitch="G",
        octave=4,
        duration="quarter",
        is_rest=False,
    )
    db.session.add(other_note)
    db.session.commit()

    client.post(
        "/auth/login",
        data={
            "username": "delete_owner",
            "password": "test123",
        },
    )

    return {
        "piece_id": piece.id,
        "note_ids": [note.id for note in notes],
        "other_piece_id": other_piece.id,
        "other_note_id": other_note.id,
    }


@pytest.mark.parametrize("delete_index", [0, 1, 2])
def test_delete_note_renumbers_positions(
    client, note_data, delete_index
):
    piece_id = note_data["piece_id"]
    note_ids = note_data["note_ids"]
    deleted_id = note_ids[delete_index]

    response = client.post(
        f"/compositions/{piece_id}/notes/{deleted_id}/delete"
    )

    assert response.status_code == 302
    assert db.session.get(Note, deleted_id) is None

    remaining = db.session.execute(
        db.select(Note)
        .where(Note.composition_id == piece_id)
        .order_by(Note.position)
    ).scalars().all()

    assert [note.position for note in remaining] == [1, 2]
    assert [note.id for note in remaining] == [
        note_id for note_id in note_ids
        if note_id != deleted_id
    ]


def test_cannot_delete_other_users_note(client, note_data):
    response = client.post(
        f"/compositions/{note_data['other_piece_id']}"
        f"/notes/{note_data['other_note_id']}/delete"
    )

    assert response.status_code == 404
    assert db.session.get(
        Note, note_data["other_note_id"]
    ) is not None


def test_cannot_delete_note_from_wrong_piece(client, note_data):
    response = client.post(
        f"/compositions/{note_data['piece_id']}"
        f"/notes/{note_data['other_note_id']}/delete"
    )

    assert response.status_code == 404


def test_delete_nonexistent_note(client, note_data):
    response = client.post(
        f"/compositions/{note_data['piece_id']}"
        "/notes/999999/delete"
    )

    assert response.status_code == 404
