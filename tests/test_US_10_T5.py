"""US-10-T5: library ownership, details, and empty state."""

import pytest
from werkzeug.security import generate_password_hash

from models import db, User, Composition


@pytest.fixture
def library_user(client):
    user = User(
        username="library_tester",
        email="library_tester@example.com",
        password_hash=generate_password_hash("test-password"),
    )
    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/auth/login",
        data={
            "username": "library_tester",
            "password": "test-password",
        },
    )
    assert response.status_code == 302
    return user


def add_piece(owner, title, key="G major", time="3/4"):
    piece = Composition(
        user_id=owner.id,
        title=title,
        key_signature=key,
        time_signature=time,
        tempo=100,
    )
    db.session.add(piece)
    db.session.commit()
    return piece


def library_html(client):
    response = client.get("/library/")
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_library_lists_only_my_pieces(client, library_user):
    other = User(
        username="other_owner",
        email="other_owner@example.com",
        password_hash=generate_password_hash("other-password"),
    )
    db.session.add(other)
    db.session.commit()

    add_piece(library_user, "My private melody")
    add_piece(other, "Someone else's secret melody")

    html = library_html(client)
    assert "My private melody" in html
    assert "Someone else" not in html


def test_library_shows_composition_details(client, library_user):
    add_piece(library_user, "Evening waltz")

    html = library_html(client)
    assert "Evening waltz" in html
    assert "G major" in html
    assert "3/4" in html


def test_empty_library_shows_required_message(client, library_user):
    html = library_html(client)
    assert "No compositions yet" in html


def test_empty_library_offers_new_composition(client, library_user):
    from html.parser import HTMLParser

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
            self.current = None

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                self.current = [dict(attrs).get("href"), ""]

        def handle_data(self, data):
            if self.current is not None:
                self.current[1] += data

        def handle_endtag(self, tag):
            if tag == "a" and self.current is not None:
                self.links.append(self.current)
                self.current = None

    parser = Links()
    parser.feed(library_html(client))

    assert any(
        href == "/compositions/new"
        and " ".join(text.split()) == "New composition"
        for href, text in parser.links
    ), "Empty library must offer a New composition link"


def test_library_sorts_by_last_edit_not_id(client, library_user):
    from datetime import datetime

    first = add_piece(library_user, "Older ID recently edited")
    second = add_piece(library_user, "Newer ID edited earlier")
    assert first.id < second.id

    first.updated_at = datetime(2026, 10, 27, 15, 30)
    second.updated_at = datetime(2026, 10, 20, 9, 0)
    db.session.commit()

    html = library_html(client)
    assert html.index(first.title) < html.index(second.title)


def test_library_shows_last_edited_date(client, library_user):
    from datetime import datetime

    piece = add_piece(library_user, "Dated melody")
    piece.updated_at = datetime(2026, 10, 25, 14, 35)
    db.session.commit()

    html = library_html(client)
    assert "Last edited: 2026-10-25 14:35" in html


def test_editing_composition_updates_timestamp(client, library_user):
    from datetime import datetime

    piece = add_piece(library_user, "Original title")
    previous = datetime(2000, 1, 1)
    piece.updated_at = previous
    db.session.commit()

    piece.title = "Revised title"
    db.session.commit()
    db.session.refresh(piece)

    assert piece.updated_at > previous


@pytest.mark.parametrize("action", ["add", "edit", "delete"])
def test_note_change_updates_composition_timestamp(
    client, library_user, action
):
    from datetime import datetime
    from models import Note

    piece = add_piece(library_user, "Note change test")
    note = Note(
        composition=piece,
        position=1,
        pitch="C",
        octave=4,
        duration="quarter",
        is_rest=False,
    )
    db.session.add(note)
    db.session.commit()

    previous = datetime(2000, 1, 1)
    piece.updated_at = previous
    db.session.commit()

    if action == "add":
        db.session.add(Note(
            composition_id=piece.id,
            position=2,
            pitch="D",
            octave=4,
            duration="quarter",
            is_rest=False,
        ))
    elif action == "edit":
        note.pitch = "E"
    else:
        db.session.delete(note)

    db.session.commit()
    db.session.refresh(piece)

    assert piece.updated_at > previous
