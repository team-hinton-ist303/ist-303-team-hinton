"""Tests for US-12-T3 (NTT-79): cross-user access attempts on every route.

Acceptance criteria covered (from story US-12, NTT-14):
  - Opening, editing, or deleting another user's composition by URL returns 404.
  - Every composition and note route checks ownership.

The main tests find every route in the compositions blueprint that takes a
composition id, so a route added later (for example deleting a whole piece)
is attacked too. Each attempt sends valid form data, so a missing ownership
check would really change the piece, and the tests confirm nothing changed.

One client is used and users log in one at a time: conftest keeps one app
context open per test, so Flask-Login's cached user would carry over between
two separate clients.
"""
import pytest
from flask import url_for
from werkzeug.security import generate_password_hash

from models import Composition, Note, User, db

PASSWORD = "test-password"
MISSING_ID = 999999

# Valid data for every POST route, so a missing check would save something.
ATTACK_DATA = {
    "title": "Taken over",
    "key_signature": "G major",
    "time_signature": "3/4",
    "tempo": "180",
    "pitch": "G",
    "octave": "5",
    "duration": "half",
    "accidental": "",
}

# Routes that existed when these tests were written; more may be found.
KNOWN_ENDPOINTS = {
    "compositions.editor",
    "compositions.edit_settings",
    "compositions.update_settings",
    "compositions.add_note",
    "compositions.update_note",
    "compositions.delete_note",
}


# --- Helpers ------------------------------------------------------------------

def make_user(username):
    user = User(username=username, email=f"{username}@example.com",
                password_hash=generate_password_hash(PASSWORD))
    db.session.add(user)
    db.session.flush()
    return user


def make_piece(user, title):
    piece = Composition(user_id=user.id, title=title, key_signature="C major",
                        time_signature="4/4", tempo=100)
    db.session.add(piece)
    db.session.flush()
    for position, pitch in enumerate(["C", "E"], start=1):
        db.session.add(Note(composition_id=piece.id, position=position, pitch=pitch,
                            octave=4, duration="quarter", is_rest=False))
    db.session.commit()
    return piece


def log_in(client, username):
    client.post("/auth/logout")
    response = client.post("/auth/login", data={"username": username, "password": PASSWORD})
    assert response.status_code == 302


@pytest.fixture
def setup(client):
    """Two users with one piece each; the client is logged in as the intruder."""
    owner = make_user("owner")
    intruder = make_user("intruder")
    owner_piece = make_piece(owner, "Owner's private piece")
    intruder_piece = make_piece(intruder, "Intruder's own piece")
    log_in(client, "intruder")
    return {
        "client": client,
        "owner_piece": owner_piece.id,
        "owner_note": owner_piece.notes[0].id,
        "intruder_piece": intruder_piece.id,
        "intruder_note": intruder_piece.notes[0].id,
    }


def composition_routes(app):
    """(endpoint, method, rule) for every compositions route that takes a composition id."""
    found = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith("compositions.") and "composition_id" in rule.arguments:
            for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
                found.append((rule.endpoint, method, rule))
    return found


def url(app, rule, composition_id, note_id):
    values = {"composition_id": composition_id}
    if "note_id" in rule.arguments:
        values["note_id"] = note_id
    with app.test_request_context():
        return url_for(rule.endpoint, **values)


def request(client, method, path):
    return client.open(path, method=method, data=ATTACK_DATA if method == "POST" else None)


def snapshot(piece_id):
    """Everything about a piece and its notes, to prove nothing changed."""
    db.session.expire_all()
    piece = db.session.get(Composition, piece_id)
    if piece is None:
        return None
    notes = db.session.execute(
        db.select(Note).where(Note.composition_id == piece_id).order_by(Note.position)
    ).scalars().all()
    return (
        (piece.user_id, piece.title, piece.key_signature, piece.time_signature, piece.tempo),
        [(n.id, n.position, n.pitch, n.octave, n.duration, n.accidental, n.is_rest) for n in notes],
    )


def label(endpoint, method):
    return f"{method} {endpoint}"


# --- The route search ---------------------------------------------------------

def test_route_search_finds_every_known_route(app):
    """Guards against the search silently finding nothing."""
    found = {endpoint for endpoint, _, _ in composition_routes(app)}
    assert KNOWN_ENDPOINTS <= found


# --- Another user's piece: always 404, never changed --------------------------

def test_every_route_returns_404_for_another_users_piece(app, setup):
    client = setup["client"]
    before = snapshot(setup["owner_piece"])

    for endpoint, method, rule in composition_routes(app):
        path = url(app, rule, setup["owner_piece"], setup["owner_note"])
        response = request(client, method, path)

        assert response.status_code == 404, label(endpoint, method)
        assert snapshot(setup["owner_piece"]) == before, f"{label(endpoint, method)} changed the piece"


def test_another_users_piece_never_appears_in_the_response(app, setup):
    client = setup["client"]

    for endpoint, method, rule in composition_routes(app):
        path = url(app, rule, setup["owner_piece"], setup["owner_note"])
        html = request(client, method, path).get_data(as_text=True)

        assert "Owner&#39;s private piece" not in html, label(endpoint, method)
        assert "Owner's private piece" not in html, label(endpoint, method)


def test_404_looks_the_same_as_a_piece_that_does_not_exist(app, setup):
    """Nothing tells an intruder that the piece exists."""
    client = setup["client"]

    for endpoint, method, rule in composition_routes(app):
        theirs = request(client, method, url(app, rule, setup["owner_piece"], setup["owner_note"]))
        missing = request(client, method, url(app, rule, MISSING_ID, MISSING_ID))

        assert theirs.status_code == missing.status_code == 404, label(endpoint, method)
        assert theirs.get_data() == missing.get_data(), label(endpoint, method)


# --- Another user's note inside my own piece ----------------------------------

def test_note_routes_reject_another_users_note_in_my_piece(app, setup):
    client = setup["client"]
    owner_before = snapshot(setup["owner_piece"])
    mine_before = snapshot(setup["intruder_piece"])

    note_routes = [r for r in composition_routes(app) if "note_id" in r[2].arguments]
    assert note_routes

    for endpoint, method, rule in note_routes:
        path = url(app, rule, setup["intruder_piece"], setup["owner_note"])
        response = request(client, method, path)

        assert response.status_code == 404, label(endpoint, method)
        assert snapshot(setup["owner_piece"]) == owner_before, label(endpoint, method)
        assert snapshot(setup["intruder_piece"]) == mine_before, label(endpoint, method)


def test_editor_ignores_another_users_note_id(setup):
    client = setup["client"]
    html = client.get(f"/compositions/{setup['intruder_piece']}",
                      query_string={"note": setup["owner_note"]}).get_data(as_text=True)

    assert 'id="delete-note-form"' not in html
    assert "Selected: note" not in html


# --- The owner still has full access (so the 404s above are about ownership) --

def test_owner_can_use_every_route(app, setup):
    client = setup["client"]
    log_in(client, "owner")

    for endpoint, method, rule in composition_routes(app):
        piece = db.session.get(Composition, setup["owner_piece"])
        if piece is None or not piece.notes:      # a delete route may have removed them
            owner = db.session.execute(db.select(User).filter_by(username="owner")).scalar_one()
            piece = make_piece(owner, "Fresh piece")
            setup["owner_piece"] = piece.id
        path = url(app, rule, piece.id, piece.notes[0].id)

        response = request(client, method, path)

        assert response.status_code != 404, label(endpoint, method)
        assert response.status_code < 500, label(endpoint, method)


def test_owner_change_saves_while_intruder_change_does_not(setup):
    client = setup["client"]
    path = f"/compositions/{setup['owner_piece']}/settings"

    client.post(path, data=ATTACK_DATA)                       # intruder
    assert snapshot(setup["owner_piece"])[0][1] == "Owner's private piece"

    log_in(client, "owner")
    client.post(path, data={**ATTACK_DATA, "title": "Renamed by owner"})
    assert snapshot(setup["owner_piece"])[0][1] == "Renamed by owner"


# --- The library only lists my own pieces -------------------------------------

def test_library_lists_only_my_pieces(setup):
    html = setup["client"].get("/library/").get_data(as_text=True)

    assert "Intruder&#39;s own piece" in html or "Intruder's own piece" in html
    assert "Owner&#39;s private piece" not in html and "Owner's private piece" not in html


def test_library_has_no_links_to_another_users_piece(setup):
    html = setup["client"].get("/library/").get_data(as_text=True)
    assert f"/compositions/{setup['owner_piece']}" not in html
