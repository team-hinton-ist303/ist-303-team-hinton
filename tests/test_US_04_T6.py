
import pytest
from werkzeug.security import generate_password_hash

from models import Composition, Note, User, db


@pytest.fixture
def piece(client):
    # Create a user and a composition
    owner = User(
        username="ntt44_owner",
        email="ntt44_owner@example.com",
        password_hash=generate_password_hash("test-password")
    )
    db.session.add(owner)
    db.session.flush()

    composition = Composition(
        user_id=owner.id,
        title="NTT-44 Test Melody",
        key_signature="C major",
        time_signature="4/4",
        tempo=100
    )
    db.session.add(composition)
    db.session.commit()

    # Log in as the composition owner
    response = client.post(
        "/auth/login",
        data={
            "username": "ntt44_owner",
            "password": "test-password"
        }
    )
    assert response.status_code == 302

    return composition


def test_added_notes_persist_in_order_after_reload(client, piece):
    # Add three notes using the real add-note route
    for pitch in ["C", "E", "G"]:
        response = client.post(
            f"/compositions/{piece.id}/notes",
            data={
                "pitch": pitch,
                "octave": "4",
                "duration": "quarter",
                "accidental": ""
            }
        )
        assert response.status_code == 302

    # Reopen the composition
    page = client.get(f"/compositions/{piece.id}")
    assert page.status_code == 200

    # Reload saved data from the database
    db.session.expire_all()

    saved_notes = (
        Note.query
        .filter_by(composition_id=piece.id)
        .order_by(Note.position)
        .all()
    )

    assert len(saved_notes) == 3
    assert [n.pitch for n in saved_notes] == ["C", "E", "G"]
    assert [n.position for n in saved_notes] == [1, 2, 3]

@pytest.mark.parametrize("pitch, octave", [
    ("G", "3"),  # Below A3
    ("D", "6"),  # Above C6
])
def test_out_of_range_notes_are_rejected(client, piece, pitch, octave):
    response = client.post(
        f"/compositions/{piece.id}/notes",
        data={
            "pitch": pitch,
            "octave": octave,
            "duration": "quarter",
            "accidental": ""
        }
    )

    # Invalid notes should be rejected
    assert response.status_code == 400

    # An error message should be displayed
    html = response.get_data(as_text=True)
    assert 'flash-error' in html

    # No invalid note should be saved
    saved_notes = Note.query.filter_by(
        composition_id=piece.id
    ).all()

    assert len(saved_notes) == 0


@pytest.mark.parametrize("pitch, octave", [
    ("A", "3"),  # Lowest allowed note
    ("C", "6"),  # Highest allowed note
])
def test_boundary_notes_are_accepted(client, piece, pitch, octave):
    response = client.post(
        f"/compositions/{piece.id}/notes",
        data={
            "pitch": pitch,
            "octave": octave,
            "duration": "quarter",
            "accidental": ""
        }
    )

    assert response.status_code == 302

    saved_notes = Note.query.filter_by(
        composition_id=piece.id
    ).all()

    assert len(saved_notes) == 1
    assert saved_notes[0].pitch == pitch
    assert saved_notes[0].octave == int(octave)

def test_saved_notes_convert_to_music21_stream(client, piece):
    from music_stream import composition_to_stream
    from music21 import stream

    # Add notes using the actual Flask route
    note_data = [
        ("C", "quarter"),
        ("E", "quarter"),
        ("G", "half"),
    ]

    for pitch, duration in note_data:
        response = client.post(
            f"/compositions/{piece.id}/notes",
            data={
                "pitch": pitch,
                "octave": "4",
                "duration": duration,
                "accidental": ""
            }
        )
        assert response.status_code == 302

    # Reload the composition from the database
    db.session.expire_all()
    saved_piece = db.session.get(Composition, piece.id)

    # Convert the saved composition to music21
    result = composition_to_stream(saved_piece)

    assert isinstance(result, stream.Stream)

    notes = list(result.notesAndRests)

    # Check the notes are in the correct order
    assert len(notes) == 3
    assert [n.pitch.nameWithOctave for n in notes] == [
        "C4", "E4", "G4"
    ]

    # Check the durations are preserved
    assert [n.duration.quarterLength for n in notes] == [
        1.0, 1.0, 2.0
    ]
