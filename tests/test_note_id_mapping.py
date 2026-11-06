"""US-06-T2: rendered notes and rests identify their database Note."""

import xml.etree.ElementTree as ET
from types import SimpleNamespace

import pytest

from render_service import composition_to_svg


def note(note_id, position, duration="quarter", is_rest=False):
    return SimpleNamespace(
        id=note_id,
        position=position,
        pitch=None if is_rest else "C",
        octave=None if is_rest else 4,
        duration=duration,
        accidental=None,
        is_rest=is_rest,
    )


def composition(notes, time_signature="4/4"):
    return SimpleNamespace(
        notes=notes,
        key_signature="C major",
        time_signature=time_signature,
        tempo=100,
    )


def rendered_elements(piece):
    root = ET.fromstring(composition_to_svg(piece))
    elements = [
        element for element in root.iter()
        if set(element.get("class", "").split()).intersection(
            {"note", "rest", "mRest"}
        )
    ]
    identifiers = [
        element.get("id") for element in root.iter()
        if element.get("id") is not None
    ]
    assert len(identifiers) == len(set(identifiers)), "Duplicate SVG IDs"
    return elements


def test_repeated_pitches_map_by_database_id_and_position():
    piece = composition([
        note(902, 2),
        note(101, 1),
        note(305, 3),
    ])

    elements = rendered_elements(piece)

    assert [element.get("data-note-id") for element in elements] == [
        "101", "902", "305",
    ]


@pytest.mark.parametrize("duration", ["quarter", "whole"])
def test_rest_maps_to_database_id(duration):
    elements = rendered_elements(composition([
        note(77, 1, duration=duration, is_rest=True),
    ]))

    assert elements
    assert all(element.get("data-note-id") == "77" for element in elements)
    assert all(
        set(element.get("class", "").split()).intersection({"rest", "mRest"})
        for element in elements
    )


@pytest.mark.parametrize("is_rest", [False, True])
def test_barline_segments_map_to_same_database_note(is_rest):
    piece = composition([
        note(101, 1, duration="half"),
        note(202, 2, duration="whole", is_rest=is_rest),
    ], time_signature="3/4")

    elements = rendered_elements(piece)
    mapped = [element.get("data-note-id") for element in elements]

    assert set(mapped) == {"101", "202"}
    segments = [
        element for element in elements
        if element.get("data-note-id") == "202"
    ]
    assert len(segments) >= 2
    assert len({element.get("id") for element in segments}) == len(segments)


def test_unsaved_sample_has_no_database_mapping():
    elements = rendered_elements(composition([note(None, 1)]))

    assert elements
    assert all(element.get("data-note-id") is None for element in elements)


def test_mapping_survives_rerender():
    piece = composition([note(101, 1), note(202, 2)])

    first = rendered_elements(piece)
    second = rendered_elements(piece)

    assert [
        (element.get("id"), element.get("data-note-id"))
        for element in first
    ] == [
        (element.get("id"), element.get("data-note-id"))
        for element in second
    ]


def test_empty_composition_returns_empty_svg():
    assert composition_to_svg(composition([])) == ""
