"""Tests for US-06-T3 (NTT-54): the editor shows the sheet music drawn by Verovio."""
from types import SimpleNamespace

import compositions
from compositions import render_editor


def note(position, pitch, octave=4, duration="quarter", accidental="", is_rest=False):
    return SimpleNamespace(position=position, pitch=pitch, octave=octave,
                           duration=duration, accidental=accidental, is_rest=is_rest)


def piece(notes):
    return SimpleNamespace(id=7, title="Sheet music test", key_signature="C major",
                           time_signature="4/4", tempo=100, notes=notes)


def staff_area(html):
    return html.split('id="staff-area"')[1].split("</section>")[0]


def render(app, composition):
    with app.test_request_context("/"):
        return render_editor(composition)


def test_editor_shows_sheet_music_svg(app):
    html = render(app, piece([note(1, "C"), note(2, "E"), note(3, "G"), note(4, "C", 5)]))
    area = staff_area(html)
    assert '<div class="staff-svg">' in area
    assert "<svg" in area
    assert "Couldn't draw" not in area


def test_no_music21_title_on_the_page(app):
    html = render(app, piece([note(1, "C")]))
    assert "Music21 Fragment" not in html


def test_note_list_still_shown_under_the_music(app):
    html = render(app, piece([note(1, "C"), note(2, "D")]))
    assert 'class="note-list"' in staff_area(html)


def test_empty_piece_shows_empty_staff_and_hint(app):
    html = render(app, piece([]))
    area = staff_area(html)
    assert '<div class="staff-svg staff-svg-empty">' in area
    assert "No notes yet." in area


def test_drawing_failure_still_opens_the_editor(app, monkeypatch):
    def broken(_composition):
        raise ValueError("verovio failed")

    monkeypatch.setattr(compositions, "composition_to_svg", broken)
    html = render(app, piece([note(1, "C")]))
    area = staff_area(html)
    assert "Couldn't draw the sheet music" in area
    assert 'class="note-list"' in area


def test_drawing_works_outside_the_main_thread():
    """Flask serves pages from worker threads; Verovio must still find its fonts there."""
    import threading
    from render_service import composition_to_svg

    result = {}

    def draw():
        try:
            result["svg"] = composition_to_svg(piece([note(1, "C")]))
        except Exception as error:  # pragma: no cover - reported below
            result["error"] = repr(error)

    worker = threading.Thread(target=draw)
    worker.start()
    worker.join()
    assert "error" not in result, result.get("error")
    assert "<svg" in result["svg"]
