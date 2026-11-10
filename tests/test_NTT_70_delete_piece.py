"""NTT-70: delete a composition and its notes with ownership protection."""

from html.parser import HTMLParser

import pytest
from werkzeug.security import generate_password_hash

from models import Composition, Note, User, db


@pytest.fixture
def pieces(test_user):
    other = User(
        username="delete_other",
        email="delete_other@example.com",
        password_hash=generate_password_hash("test-password"),
    )
    db.session.add(other)
    db.session.flush()

    result = []
    for owner, title in [
        (test_user, "Delete this piece"),
        (test_user, "Keep my other piece"),
        (other, "Other user's piece"),
    ]:
        piece = Composition(
            user_id=owner.id,
            title=title,
            key_signature="C major",
            time_signature="4/4",
            tempo=100,
        )
        db.session.add(piece)
        db.session.flush()
        for position in (1, 2):
            db.session.add(Note(
                composition_id=piece.id,
                position=position,
                pitch="C",
                octave=4,
                duration="quarter",
                is_rest=False,
            ))
        result.append(piece.id)

    db.session.commit()
    return result


def snapshot():
    db.session.expire_all()
    pieces = db.session.execute(
        db.select(Composition).order_by(Composition.id)
    ).scalars().all()
    notes = db.session.execute(
        db.select(Note).order_by(Note.id)
    ).scalars().all()
    return (
        [(p.id, p.user_id, p.title) for p in pieces],
        [(n.id, n.composition_id, n.position, n.pitch) for n in notes],
    )


def test_delete_removes_piece_and_its_notes_only(logged_in_client, pieces):
    target, keep, foreign = pieces
    before_pieces, before_notes = snapshot()

    response = logged_in_client.post(f"/compositions/{target}/delete")

    assert response.status_code == 302
    assert response.headers["Location"] == "/library/"
    after_pieces, after_notes = snapshot()
    assert after_pieces == [p for p in before_pieces if p[0] != target]
    assert after_notes == [n for n in before_notes if n[1] != target]

    page = logged_in_client.get(response.headers["Location"])
    html = page.get_data(as_text=True)
    assert page.status_code == 200
    assert "Piece deleted" in html
    assert "Delete this piece" not in html
    assert "Keep my other piece" in html

    assert logged_in_client.get(f"/compositions/{target}").status_code == 404


def test_empty_piece_can_be_deleted(logged_in_client, test_user):
    piece = Composition(
        user_id=test_user.id,
        title="Empty delete test",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )
    db.session.add(piece)
    db.session.commit()
    piece_id = piece.id

    assert logged_in_client.post(
        f"/compositions/{piece_id}/delete"
    ).status_code == 302
    db.session.expire_all()
    assert db.session.get(Composition, piece_id) is None


def test_foreign_piece_returns_404_and_preserves_data(logged_in_client, pieces):
    before = snapshot()
    response = logged_in_client.post(f"/compositions/{pieces[2]}/delete")
    assert response.status_code == 404
    assert snapshot() == before


def test_missing_piece_returns_404_and_preserves_data(logged_in_client, pieces):
    before = snapshot()
    response = logged_in_client.post(
        f"/compositions/{max(pieces) + 100}/delete"
    )
    assert response.status_code == 404
    assert snapshot() == before


def test_get_cannot_delete_piece(logged_in_client, pieces):
    before = snapshot()
    response = logged_in_client.get(f"/compositions/{pieces[0]}/delete")
    assert response.status_code == 405
    assert snapshot() == before


def test_logged_out_user_cannot_delete(client, pieces):
    before = snapshot()
    response = client.post(f"/compositions/{pieces[0]}/delete")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
    assert snapshot() == before


class DeleteForm(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.form = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form" and attrs.get("id") == "delete-piece-form":
            self.form = attrs


def test_header_has_post_form_and_confirmation(logged_in_client, pieces):
    response = logged_in_client.get(f"/compositions/{pieces[0]}")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    header = html.split('class="editor-header"', 1)[1].split("</header>", 1)[0]
    form = DeleteForm(header).form

    assert form is not None
    assert form["method"].lower() == "post"
    assert form["action"] == f"/compositions/{pieces[0]}/delete"
    assert form["onsubmit"] == (
        "return confirm('Delete this piece and all its notes? "
        "This cannot be undone.');"
    )
    assert "Delete piece</button>" in header


def test_preview_has_no_delete_piece_control(logged_in_client):
    response = logged_in_client.get("/compositions/preview")
    assert response.status_code == 200
    assert DeleteForm(response.get_data(as_text=True)).form is None
