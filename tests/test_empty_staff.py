"""Tests for US-06-T4 (NTT-55): a piece with no notes shows an empty staff
with its clef, key signature, time signature and tempo."""
import re
from types import SimpleNamespace

import pytest

import compositions
from compositions import render_editor
from render_service import composition_to_svg, empty_staff_svg


def piece(key="C major", time="4/4", tempo=100, notes=None):
    return SimpleNamespace(id=9, title="Empty staff test", key_signature=key,
                           time_signature=time, tempo=tempo, notes=notes or [])


def classes(svg):
    return set(re.findall(r'<g[^>]*class="([a-zA-Z]+)"', svg))


def staff_area(html):
    return html.split('id="staff-area"')[1].split("</section>")[0]


def render(app, composition):
    with app.test_request_context("/"):
        return render_editor(composition)


# --- render_service.empty_staff_svg -------------------------------------------

def test_empty_staff_has_clef_time_signature_and_tempo():
    svg = empty_staff_svg(piece())
    assert "<svg" in svg
    found = classes(svg)
    assert {"staff", "clef", "meterSig", "tempo"} <= found


def test_empty_staff_has_no_notes_or_rests():
    found = classes(empty_staff_svg(piece()))
    assert not found & {"note", "rest", "mRest"}


@pytest.mark.parametrize("key, sharps_or_flats", [("D major", 2), ("F major", 1), ("Bb major", 2), ("A minor", 0)])
def test_empty_staff_shows_the_key_signature(key, sharps_or_flats):
    svg = empty_staff_svg(piece(key=key))
    assert len(re.findall(r'class="keyAccid"', svg)) == sharps_or_flats


@pytest.mark.parametrize("time", ["2/4", "3/4", "6/8"])
def test_empty_staff_works_for_other_time_signatures(time):
    assert "meterSig" in classes(empty_staff_svg(piece(time=time)))


def test_composition_to_svg_still_returns_nothing_for_an_empty_piece():
    """NTT-52's contract is unchanged: the empty staff is a separate function."""
    assert composition_to_svg(piece()) == ""


# --- Editor page ----------------------------------------------------------------

def test_editor_shows_empty_staff_above_the_hint(app):
    area = staff_area(render(app, piece(key="D major", time="3/4")))
    assert area.index('class="staff-svg staff-svg-empty"') < area.index("No notes yet.")
    assert "<svg" in area
    assert 'class="note-list"' not in area


def test_editor_with_notes_does_not_show_empty_staff(app):
    note = SimpleNamespace(position=1, pitch="C", octave=4, duration="quarter",
                           accidental="", is_rest=False)
    area = staff_area(render(app, piece(notes=[note])))
    assert "staff-svg-empty" not in area
    assert 'class="note-list"' in area


def test_empty_staff_failure_still_shows_hint(app, monkeypatch):
    def broken(_composition):
        raise ValueError("verovio failed")

    monkeypatch.setattr(compositions, "empty_staff_svg", broken)
    area = staff_area(render(app, piece()))
    assert "<svg" not in area
    assert "No notes yet." in area


def test_new_piece_shows_empty_staff_after_create(logged_in_client):
    response = logged_in_client.post("/compositions/new", data={
        "title": "Fresh piece", "key_signature": "G major", "time_signature": "3/4", "tempo": "90"})
    assert response.status_code == 302

    html = logged_in_client.get(response.headers["Location"]).get_data(as_text=True)
    area = staff_area(html)
    assert "staff-svg-empty" in area
    assert "No notes yet." in area
