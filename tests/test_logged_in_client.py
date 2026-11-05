"""Tests for US-02-T6 (NTT-111): the shared `logged_in_client` fixture in conftest.py."""
from models import Composition, db


def test_logged_in_client_can_open_a_protected_page(logged_in_client):
    response = logged_in_client.get("/library/")
    assert response.status_code == 200


def test_plain_client_is_still_logged_out(client):
    response = client.get("/library/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_logged_in_client_acts_as_test_user(logged_in_client, test_user):
    piece = Composition(
        user_id=test_user.id,
        title="Fixture piece",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )
    db.session.add(piece)
    db.session.commit()

    response = logged_in_client.get(f"/compositions/{piece.id}")
    assert response.status_code == 200
    assert "Fixture piece" in response.get_data(as_text=True)
