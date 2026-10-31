"""Tests for US-04-T4 (NTT-42): treble-clef range validation (A3 to C6).

Acceptance criterion covered (from story US-04, NTT-6):
  - Notes outside the treble-clef range (A3–C6) are rejected with a message.

Agreed at the Oct 28 stand-up: the check uses the note it actually becomes,
so the key signature counts (A3 in a key with A-flat is A-flat 3, out of range).

`note_range_error()` returns an error message, or None when the note is allowed.
The add-note route (NTT-41) calls it before saving.
"""
import itertools

import pytest
from music21 import pitch as m21pitch

from compositions import (
    ACCIDENTALS, KEY_SIGNATURES, OCTAVES, PITCHES, RANGE_HIGH, RANGE_LOW,
    effective_accidental, midi_number, note_range_error,
)


def ok(pitch, octave, accidental="", key="C major"):
    return note_range_error(pitch, octave, accidental, key) is None


# --- Inside the range ---------------------------------------------------------

@pytest.mark.parametrize("pitch, octave", [
    ("A", 3),   # lowest note
    ("B", 3),
    ("C", 4),   # middle C
    ("G", 5),
    ("B", 5),
    ("C", 6),   # highest note
])
def test_notes_inside_range_are_allowed(pitch, octave):
    assert ok(pitch, octave)


def test_range_ends_match_palette():
    assert ok(*RANGE_LOW)
    assert ok(*RANGE_HIGH)


# --- Outside the range --------------------------------------------------------

@pytest.mark.parametrize("pitch, octave", [
    ("G", 3),   # one step below A3
    ("C", 3),
    ("D", 6),   # one step above C6
    ("C", 7),
])
def test_notes_outside_range_are_rejected(pitch, octave):
    assert not ok(pitch, octave)


# --- Accidentals at the edges -------------------------------------------------

@pytest.mark.parametrize("pitch, octave, accidental, allowed", [
    ("A", 3, "flat", False),     # A-flat 3 is below A3
    ("G", 3, "sharp", False),    # G-sharp 3 is below A3
    ("A", 3, "sharp", True),
    ("A", 3, "natural", True),
    ("C", 6, "sharp", False),    # C-sharp 6 is above C6
    ("C", 6, "flat", True),      # C-flat 6 sounds as B5
    ("B", 5, "sharp", True),     # B-sharp 5 sounds as C6
    ("C", 6, "natural", True),
])
def test_accidentals_at_range_edges(pitch, octave, accidental, allowed):
    assert ok(pitch, octave, accidental) is allowed


# --- Key signature: check the note it actually becomes ------------------------

@pytest.mark.parametrize("pitch, octave, accidental, key, allowed", [
    ("A", 3, "", "Eb major", False),        # key adds a flat: A-flat 3, out
    ("A", 3, "natural", "Eb major", True),  # natural cancels the key: A3, in
    ("A", 3, "", "C major", True),
    ("C", 6, "", "D major", False),         # key adds a sharp: C-sharp 6, out
    ("C", 6, "natural", "D major", True),
    ("C", 6, "", "Gb major", True),         # C-flat 6 sounds as B5, in
    ("F", 4, "", "G major", True),          # middle of the range, key does not matter
])
def test_key_signature_is_applied(pitch, octave, accidental, key, allowed):
    assert ok(pitch, octave, accidental, key) is allowed


# --- The message --------------------------------------------------------------

def test_message_names_the_note_and_the_range():
    message = note_range_error("G", 3, "", "C major")
    assert message == "G3 is below the treble-clef range (A3 to C6)."


def test_message_says_above_for_high_notes():
    message = note_range_error("D", 6, "", "C major")
    assert message == "D6 is above the treble-clef range (A3 to C6)."


def test_message_shows_the_key_signature_accidental():
    """So the user can see why A3 was rejected in E-flat major."""
    assert note_range_error("A", 3, "", "Eb major") == (
        "A♭3 is below the treble-clef range (A3 to C6)."
    )


# --- Rests and form input -----------------------------------------------------

def test_rests_always_pass():
    assert note_range_error(None, None, "", "C major") is None


def test_octave_from_a_form_is_a_string():
    assert ok("C", "4")
    assert not ok("C", "7")


@pytest.mark.parametrize("pitch, octave, accidental", [
    ("H", 4, ""),           # not a note letter
    ("C", "", ""),          # missing octave
    ("C", "four", ""),      # not a number
    ("C", 4, "double"),     # unknown accidental
])
def test_bad_input_gives_a_message_not_a_crash(pitch, octave, accidental):
    message = note_range_error(pitch, octave, accidental, "C major")
    assert isinstance(message, str) and message


def test_missing_accidental_counts_as_key_signature():
    assert note_range_error("A", 3, None, "Eb major") is not None


# --- Every palette choice agrees with music21 ---------------------------------

def test_every_palette_combination_matches_music21():
    """Checks all pitches x octaves x accidentals x keys against music21's pitch numbers."""
    low = m21pitch.Pitch(f"{RANGE_LOW[0]}{RANGE_LOW[1]}").midi
    high = m21pitch.Pitch(f"{RANGE_HIGH[0]}{RANGE_HIGH[1]}").midi
    m21_acc = {"": "", "natural": "", "sharp": "#", "flat": "-"}
    keys = [key for key, _ in KEY_SIGNATURES]
    accidentals = [value for value, _, _ in ACCIDENTALS]

    for p, o, a, k in itertools.product(PITCHES, OCTAVES, accidentals, keys):
        acc = effective_accidental(p, a, k)
        expected = low <= m21pitch.Pitch(f"{p}{m21_acc[acc]}{o}").midi <= high
        assert ok(p, o, a, k) is expected, (p, o, a, k)
        assert midi_number(p, o, acc) == m21pitch.Pitch(f"{p}{m21_acc[acc]}{o}").midi
