
from types import SimpleNamespace

from music21 import key, meter, tempo
from music_stream import composition_to_stream


def make_note(position, pitch, octave, duration,
              accidental=None, is_rest=False):
    return SimpleNamespace(
        position=position,
        pitch=pitch,
        octave=octave,
        duration=duration,
        accidental=accidental,
        is_rest=is_rest
    )


def test_note_order_and_duration():
    composition = SimpleNamespace(
        notes=[
            make_note(2, "G", 4, "half"),
            make_note(1, "C", 4, "quarter")
        ]
    )

    result = composition_to_stream(composition)
    notes = list(result.notesAndRests)

    assert len(notes) == 2
    assert notes[0].pitch.nameWithOctave == "C4"
    assert notes[1].pitch.nameWithOctave == "G4"
    assert notes[0].duration.quarterLength == 1
    assert notes[1].duration.quarterLength == 2


def test_accidentals_and_rest():
    composition = SimpleNamespace(
        notes=[
            make_note(1, "F", 4, "eighth", "sharp"),
            make_note(2, "B", 4, "half", "flat"),
            make_note(3, None, None, "quarter", is_rest=True)
        ]
    )

    result = composition_to_stream(composition)
    notes = list(result.notesAndRests)

    assert len(notes) == 3
    assert notes[0].pitch.nameWithOctave == "F#4"
    assert notes[1].pitch.nameWithOctave == "B-4"
    assert notes[2].isRest
    assert notes[2].duration.quarterLength == 1


def test_empty_composition():
    composition = SimpleNamespace(notes=[])

    result = composition_to_stream(composition)

    assert len(list(result.notesAndRests)) == 0


def test_composition_metadata():
    composition = SimpleNamespace(
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
        notes=[
            make_note(1, "C", 4, "quarter")
        ]
    )

    result = composition_to_stream(composition)

    music_key = result.getElementsByClass(key.Key).first()
    time_sig = result.getElementsByClass(meter.TimeSignature).first()
    tempo_mark = result.getElementsByClass(tempo.MetronomeMark).first()

    assert music_key.tonic.name == "C"
    assert music_key.mode == "major"
    assert time_sig.ratioString == "4/4"
    assert tempo_mark.number == 100
    assert len(list(result.notesAndRests)) == 1


def test_flat_key_signature():
    composition = SimpleNamespace(
        key_signature="Bb major",
        time_signature="3/4",
        tempo=120,
        notes=[]
    )

    result = composition_to_stream(composition)

    music_key = result.getElementsByClass(key.Key).first()

    assert music_key.tonic.name == "B-"
    assert music_key.mode == "major"

def test_real_database_composition(app):
    from models import User, Composition, Note, db

    with app.app_context():
        user = User(
            username="music_tester",
            email="music_tester@example.com",
            password_hash="test-hash"
        )

        composition = Composition(
            owner=user,
            title="Test Melody",
            key_signature="C major",
            time_signature="4/4",
            tempo=100
        )

        first_note = Note(
            composition=composition,
            position=1,
            pitch="C",
            octave=4,
            duration="quarter"
        )

        second_note = Note(
            composition=composition,
            position=2,
            pitch="G",
            octave=4,
            duration="half"
        )

        db.session.add_all([
            user, composition, first_note, second_note
        ])
        db.session.commit()

        saved_composition = db.session.get(
            Composition, composition.id
        )

        result = composition_to_stream(saved_composition)
        notes = list(result.notesAndRests)

        assert len(notes) == 2
        assert notes[0].pitch.nameWithOctave == "C4"
        assert notes[1].pitch.nameWithOctave == "G4"
        assert notes[0].duration.quarterLength == 1
        assert notes[1].duration.quarterLength == 2
