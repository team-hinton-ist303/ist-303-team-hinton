"""US-12-T1: ownership checks for existing compositions."""

import pytest
from werkzeug.security import generate_password_hash

from models import Composition, User, db


@pytest.fixture
def ownership_data(client):
    owner = User(
        username="piece_owner",
        email="owner@example.com",
        password_hash=generate_password_hash("test-password"),
    )
    other = User(
        username="other_user",
        email="other@example.com",
        password_hash=generate_password_hash("test-password"),
    )
    db.session.add_all([owner, other])
    db.session.flush()

    piece = Composition(
        user_id=owner.id,
        title="Private ownership test",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )
    db.session.add(piece)
    db.session.commit()
    return owner, other, piece


def login(client, user):
    response = client.post(
        "/auth/login",
        data={"username": user.username, "password": "test-password"},
    )
    assert response.status_code == 302


def test_owner_can_open_composition(client, ownership_data):
    owner, _, piece = ownership_data
    login(client, owner)

    response = client.get(f"/compositions/{piece.id}")

    assert response.status_code == 200
    assert piece.title in response.get_data(as_text=True)


def test_other_user_gets_404(client, ownership_data):
    _, other, piece = ownership_data
    login(client, other)

    response = client.get(f"/compositions/{piece.id}")

    assert response.status_code == 404
    assert piece.title not in response.get_data(as_text=True)


def test_missing_composition_gets_404(client, ownership_data):
    owner, _, piece = ownership_data
    login(client, owner)

    response = client.get(f"/compositions/{piece.id + 1}")

    assert response.status_code == 404


def test_logged_out_user_redirects_to_login(client, ownership_data):
    _, _, piece = ownership_data

    response = client.get(f"/compositions/{piece.id}")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
