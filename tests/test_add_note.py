"""NTT-41: add-note validation, ordering, rests, and ownership."""

import pytest
from werkzeug.security import generate_password_hash

from models import Composition, Note, User, db


VALID = {
    "pitch": "C",
    "octave": "4",
    "duration": "quarter",
    "accidental": "",
}


@pytest.fixture
def piece(client):
    owner = User(
        username="note_owner",
        email="note_owner@example.com",
        password_hash=generate_password_hash("test-password"),
    )
    db.session.add(owner)
    db.session.flush()

    composition = Composition(
        user_id=owner.id,
        title="Add-note test",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )
    db.session.add(composition)
    db.session.commit()

    response = client.post(
        "/auth/login",
        data={"username": owner.username, "password": "test-password"},
    )
    assert response.status_code == 302
    return composition


def post_note(client, piece, data=None):
    return client.post(
        f"/compositions/{piece.id}/notes",
        data=VALID if data is None else data,
    )


@pytest.mark.parametrize(
    "duration", ["whole", "half", "quarter", "eighth", "16th"]
)
def test_valid_note_is_saved_and_redirects(client, piece, duration):
    response = post_note(client, piece, {**VALID, "duration": duration})

    assert response.status_code == 302
    assert response.headers["Location"] == f"/compositions/{piece.id}"
    saved = Note.query.one()
    assert saved.composition_id == piece.id
    assert saved.position == 1
    assert (saved.pitch, saved.octave, saved.duration) == ("C", 4, duration)
    assert not saved.is_rest

    page = client.get(response.headers["Location"])
    assert page.status_code == 200
    assert "Note added" in page.get_data(as_text=True)


def test_appends_after_highest_position_in_this_piece(client, piece):
    other_piece = Composition(
        user_id=piece.user_id,
        title="Other piece",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )
    db.session.add(other_piece)
    db.session.flush()
    existing = Note(
        composition_id=piece.id, position=5,
        pitch="D", octave=4, duration="half", is_rest=False,
    )
    db.session.add_all([
        existing,
        Note(
            composition_id=other_piece.id, position=99,
            pitch="E", octave=4, duration="whole", is_rest=False,
        ),
    ])
    db.session.commit()

    assert post_note(client, piece).status_code == 302

    notes = Note.query.filter_by(
        composition_id=piece.id
    ).order_by(Note.position).all()
    assert [note.position for note in notes] == [5, 6]
    assert (notes[0].pitch, notes[0].duration) == ("D", "half")


def test_rest_saves_without_pitch_fields(client, piece):
    response = post_note(
        client, piece, {"is_rest": "1", "duration": "quarter"}
    )

    assert response.status_code == 302
    saved = Note.query.one()
    assert saved.is_rest
    assert saved.position == 1
    assert saved.pitch is None
    assert saved.octave is None
    assert saved.accidental is None


@pytest.mark.parametrize("changes", [
    {"pitch": "G", "octave": "3"},
    {"pitch": "D", "octave": "6"},
    {"pitch": "A", "octave": "3", "accidental": "flat"},
    {"pitch": "C", "octave": "6", "accidental": "sharp"},
    {"pitch": "H"},
    {"pitch": ""},
    {"octave": "invalid"},
    {"accidental": "unknown"},
    {"duration": "unknown"},
    {"duration": ""},
])
def test_invalid_note_returns_400_without_saving(client, piece, changes):
    response = post_note(client, piece, {**VALID, **changes})

    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert piece.title in html
    assert 'class="flash flash-error"' in html
    assert Note.query.count() == 0


def test_missing_pitch_is_rejected(client, piece):
    data = {key: value for key, value in VALID.items() if key != "pitch"}
    assert post_note(client, piece, data).status_code == 400
    assert Note.query.count() == 0


def test_rest_still_requires_valid_duration(client, piece):
    response = post_note(
        client, piece, {"is_rest": "1", "duration": "unknown"}
    )
    assert response.status_code == 400
    assert Note.query.count() == 0


@pytest.mark.parametrize("accidental, expected", [
    ("", "sharp"),
    ("natural", "natural"),
    ("flat", "flat"),
])
def test_accidental_matches_key_or_explicit_choice(
    client, piece, accidental, expected
):
    piece.key_signature = "G major"
    db.session.commit()

    response = post_note(client, piece, {
        **VALID, "pitch": "F", "accidental": accidental,
    })

    assert response.status_code == 302
    assert Note.query.one().accidental == expected


def test_key_signature_can_make_boundary_note_invalid(client, piece):
    piece.key_signature = "Eb major"
    db.session.commit()

    response = post_note(
        client, piece, {**VALID, "pitch": "A", "octave": "3"}
    )

    assert response.status_code == 400
    assert Note.query.count() == 0


def test_another_users_piece_returns_404(client, piece):
    other = User(
        username="another_owner",
        email="another_owner@example.com",
        password_hash=generate_password_hash("test-password"),
    )
    db.session.add(other)
    db.session.flush()
    piece.user_id = other.id
    db.session.commit()

    assert post_note(client, piece).status_code == 404
    assert Note.query.count() == 0


def test_missing_piece_returns_404(client, piece):
    response = client.post(
        f"/compositions/{piece.id + 1000}/notes", data=VALID
    )
    assert response.status_code == 404
    assert Note.query.count() == 0


def test_logged_out_user_cannot_add_note(client, piece):
    client.post("/auth/logout")

    response = post_note(client, piece)

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
    assert Note.query.count() == 0


@pytest.mark.parametrize("duration", [
    "whole",
    "half",
    "quarter",
    "eighth",
    "16th",
])
def test_rest_supported_for_every_duration(client, piece, duration):
    response = client.post(
        f"/compositions/{piece.id}/notes",
        data={
            "is_rest": "1",
            "duration": duration,
        }
    )

    assert response.status_code == 302

    saved = Note.query.filter_by(
        composition_id=piece.id
    ).one()

    assert saved.is_rest is True
    assert saved.duration == duration
    assert saved.pitch is None
    assert saved.octave is None
    assert saved.accidental is None
