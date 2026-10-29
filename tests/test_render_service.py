
from types import SimpleNamespace

from render_service import composition_to_svg


def make_note(position, pitch, octave, duration="quarter",
              accidental=None, is_rest=False):
    return SimpleNamespace(
        position=position,
        pitch=pitch,
        octave=octave,
        duration=duration,
        accidental=accidental,
        is_rest=is_rest
    )


def make_composition(notes, key_signature="C major",
                     time_signature="4/4", tempo=100):
    return SimpleNamespace(
        notes=notes,
        key_signature=key_signature,
        time_signature=time_signature,
        tempo=tempo
    )


def test_svg_generated_with_notes():
    composition = make_composition([
        make_note(1, "C", 4),
        make_note(2, "E", 4),
        make_note(3, "G", 4),
        make_note(4, "C", 5)
    ])

    svg = composition_to_svg(composition)

    assert isinstance(svg, str)
    assert "<svg" in svg
    assert "</svg>" in svg


def test_svg_generated_with_rest():
    composition = make_composition([
        make_note(1, "C", 4),
        make_note(2, None, None, is_rest=True),
        make_note(3, "E", 4),
        make_note(4, "G", 4)
    ])

    svg = composition_to_svg(composition)

    assert "<svg" in svg
    assert "</svg>" in svg


def test_svg_with_flat_key_and_three_four_time():
    composition = make_composition(
        notes=[
            make_note(1, "B", 4, accidental="flat"),
            make_note(2, "D", 5),
            make_note(3, "F", 5)
        ],
        key_signature="Bb major",
        time_signature="3/4",
        tempo=120
    )

    svg = composition_to_svg(composition)

    assert "<svg" in svg
    assert "</svg>" in svg


def test_empty_composition():
    composition = make_composition([])

    svg = composition_to_svg(composition)

    assert svg == ""
