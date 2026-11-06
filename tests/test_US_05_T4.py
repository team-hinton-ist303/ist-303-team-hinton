"""Tests for US-05-T4 (NTT-51): rests.

Task: add rest, rest in conversion, rest in rendered SVG.

Acceptance criteria covered (from story US-05, NTT-7):
  - A Rest option is available for every duration.
  - Rests are saved in order with notes and appear on the staff.
  - Rests convert to music21 `Rest` objects.

Rests are added through the real add-note route (POST /compositions/<id>/notes),
then read back from the database, converted with music_stream, and drawn with
render_service, so every step works on the same saved composition.
"""
import re

import pytest
from music21 import note as m21note
from werkzeug.security import generate_password_hash

from compositions import DURATIONS
from models import Composition, Note, User, db
from music_stream import composition_to_stream
from render_service import composition_to_svg

PASSWORD = "test-password"
DURATION_VALUES = [value for value, _ in DURATIONS]
QUARTER_LENGTHS = {"whole": 4.0, "half": 2.0, "quarter": 1.0, "eighth": 0.5, "16th": 0.25}


@pytest.fixture
def piece(client):
    """A composition owned by a logged-in user. Can switch to the shared fixture once NTT-111 lands."""
    owner = User(username="rest_owner", email="rest_owner@example.com",
                 password_hash=generate_password_hash(PASSWORD))
    db.session.add(owner)
    db.session.flush()
    composition = Composition(user_id=owner.id, title="Rest test", key_signature="C major",
                              time_signature="4/4", tempo=100)
    db.session.add(composition)
    db.session.commit()

    response = client.post("/auth/login", data={"username": "rest_owner", "password": PASSWORD})
    assert response.status_code == 302
    return composition


def add_rest(client, piece, duration="quarter", **extra):
    return client.post(f"/compositions/{piece.id}/notes",
                       data={"is_rest": "1", "duration": duration, **extra})


def add_note(client, piece, pitch="C", octave="4", duration="quarter"):
    return client.post(f"/compositions/{piece.id}/notes",
                       data={"pitch": pitch, "octave": octave, "duration": duration, "accidental": ""})


def saved_notes(piece):
    db.session.expire_all()
    return Note.query.filter_by(composition_id=piece.id).order_by(Note.position).all()


def reloaded(piece):
    db.session.expire_all()
    return db.session.get(Composition, piece.id)


def svg_order(svg):
    """'note' and 'rest' in the order Verovio drew them on the staff.

    A rest that fills a whole bar is drawn as a measure rest (class "mRest"),
    so it counts as a rest. The tests keep rests inside one bar: music21 splits
    anything that crosses a bar line into two pieces.
    """
    found = re.findall(r'<g[^>]*class="(note|rest|mRest)"', svg)
    return ["rest" if item == "mRest" else item for item in found]


# --- Add rest: a Rest option for every duration -------------------------------

def test_editor_offers_rest_and_every_duration(client, piece):
    html = client.get(f"/compositions/{piece.id}").get_data(as_text=True)

    assert 'name="is_rest"' in html
    for duration in DURATION_VALUES:
        assert f'name="duration" id="duration-{duration}" value="{duration}"' in html


@pytest.mark.parametrize("duration", DURATION_VALUES)
def test_rest_can_be_added_for_every_duration(client, piece, duration):
    response = add_rest(client, piece, duration)

    assert response.status_code == 302
    rest = saved_notes(piece)[0]
    assert rest.is_rest
    assert rest.duration == duration
    assert (rest.pitch, rest.octave, rest.accidental) == (None, None, None)


def test_rest_ignores_pitch_fields_sent_with_it(client, piece):
    """Even an out-of-range or bad pitch is dropped when Rest is ticked."""
    response = add_rest(client, piece, pitch="H", octave="9", accidental="sharp")

    assert response.status_code == 302
    rest = saved_notes(piece)[0]
    assert rest.is_rest and rest.pitch is None and rest.octave is None


def test_rest_with_bad_duration_is_rejected(client, piece):
    assert add_rest(client, piece, "dotted-whole").status_code == 400
    assert saved_notes(piece) == []


# --- Saved in order with notes ------------------------------------------------

def test_rests_are_saved_in_order_with_notes(client, piece):
    add_note(client, piece, "C")
    add_rest(client, piece, "half")
    add_note(client, piece, "E")
    add_rest(client, piece, "eighth")

    notes = saved_notes(piece)
    assert [n.position for n in notes] == [1, 2, 3, 4]
    assert [("rest" if n.is_rest else n.pitch) for n in notes] == ["C", "rest", "E", "rest"]


def test_composition_can_start_with_a_rest(client, piece):
    add_rest(client, piece)
    add_note(client, piece, "G")

    assert [n.is_rest for n in saved_notes(piece)] == [True, False]


def test_editor_lists_rests_in_order(client, piece):
    add_note(client, piece, "C")
    add_rest(client, piece, "half")
    add_note(client, piece, "E")

    html = client.get(f"/compositions/{piece.id}").get_data(as_text=True)
    note_list = html.split('class="note-list"', 1)[1].split("</ol>", 1)[0]
    # Each chip's label, ignoring any tags around it (chips are links since NTT-62).
    chips = [
        re.sub(r"<[^>]+>", "", chip.split('<span class="note-chip-duration"', 1)[0].split(">", 1)[1]).strip()
        for chip in note_list.split('<li class="note-chip')[1:]
    ]

    assert chips == ["C4", "Rest", "E4"]
    assert "half" in note_list


# --- Rest in conversion: music21 Rest objects ---------------------------------

def test_rest_converts_to_music21_rest(client, piece):
    add_rest(client, piece)

    converted = list(composition_to_stream(reloaded(piece)).notesAndRests)

    assert len(converted) == 1
    assert isinstance(converted[0], m21note.Rest)


@pytest.mark.parametrize("duration", DURATION_VALUES)
def test_rest_keeps_its_duration_in_conversion(client, piece, duration):
    add_rest(client, piece, duration)

    rest = list(composition_to_stream(reloaded(piece)).notesAndRests)[0]

    assert isinstance(rest, m21note.Rest)
    assert rest.duration.type == duration
    assert rest.duration.quarterLength == QUARTER_LENGTHS[duration]


def test_conversion_keeps_rests_in_order_with_notes(client, piece):
    add_note(client, piece, "C")
    add_rest(client, piece, "half")
    add_note(client, piece, "E")

    converted = list(composition_to_stream(reloaded(piece)).notesAndRests)

    assert [type(item).__name__ for item in converted] == ["Note", "Rest", "Note"]
    assert converted[0].nameWithOctave == "C4"
    assert converted[2].nameWithOctave == "E4"


def test_rest_is_a_rest_not_a_silent_note(client, piece):
    add_rest(client, piece)

    rest = list(composition_to_stream(reloaded(piece)).notesAndRests)[0]

    assert rest.isRest
    assert not isinstance(rest, m21note.Note)


# --- Rest in rendered SVG: appears on the staff -------------------------------

def test_rest_appears_in_rendered_svg(client, piece):
    add_rest(client, piece)

    svg = composition_to_svg(reloaded(piece))

    assert "<svg" in svg
    assert svg_order(svg) == ["rest"]


def test_svg_has_one_rest_per_saved_rest(client, piece):
    add_rest(client, piece, "quarter")
    add_note(client, piece, "D")
    add_rest(client, piece, "eighth")
    add_rest(client, piece, "eighth")

    svg_items = svg_order(composition_to_svg(reloaded(piece)))

    assert svg_items.count("rest") == 3
    assert svg_items.count("note") == 1


def test_svg_draws_rests_in_order_with_notes(client, piece):
    add_note(client, piece, "C")
    add_rest(client, piece, "half")
    add_note(client, piece, "E")
    add_rest(client, piece, "quarter")

    assert svg_order(composition_to_svg(reloaded(piece))) == ["note", "rest", "note", "rest"]


@pytest.mark.parametrize("duration", DURATION_VALUES)
def test_every_rest_duration_renders(client, piece, duration):
    add_rest(client, piece, duration)

    assert svg_order(composition_to_svg(reloaded(piece))) == ["rest"]


def test_whole_bar_rest_is_drawn_as_a_measure_rest(client, piece):
    add_rest(client, piece, "whole")   # fills a 4/4 bar

    svg = composition_to_svg(reloaded(piece))

    assert re.search(r'<g[^>]*class="mRest"', svg)
