"""Tests for US-01-T4 (NTT-29): registration (story US-01, NTT-3).

Acceptance criteria covered:
  - A unique username and email with an 8+ character password creates the account and logs the user in.
  - A duplicate username or email shows an error and no account is created.
  - Missing or invalid fields show a message and no account is created.
  - Passwords are stored hashed, never in plain text.

Uses the shared `app` and `client` fixtures from conftest.py.

Assumes the register route from US-01-T2/T3 is POST /auth/register with form
fields `username`, `email`, and `password`. Until that route is merged, every
test in this file is skipped instead of failing.
"""
import pytest
from werkzeug.security import check_password_hash

from models import User

REGISTER_URL = "/auth/register"
PASSWORD = "correct-horse-9"


@pytest.fixture(autouse=True)
def require_register_route(app):
    """Skip these tests until the register route (US-01-T2) exists."""
    if not any(rule.rule == REGISTER_URL for rule in app.url_map.iter_rules()):
        pytest.skip(f"{REGISTER_URL} not built yet (US-01-T2)")
    app.config["WTF_CSRF_ENABLED"] = False  # in case the form uses Flask-WTF


def register(client, username="ryan", email="ryan@example.com", password=PASSWORD):
    return client.post(REGISTER_URL, data={
        "username": username, "email": email, "password": password,
    })


# --- Success ------------------------------------------------------------------

def test_register_form_loads(client):
    assert client.get(REGISTER_URL).status_code == 200


def test_register_success_creates_user(client):
    response = register(client)

    assert response.status_code in (200, 302, 303)
    user = User.query.filter_by(username="ryan").one()
    assert user.email == "ryan@example.com"


def test_register_success_logs_user_in(client):
    register(client)
    user = User.query.filter_by(username="ryan").one()

    with client.session_transaction() as session:
        assert session.get("_user_id") == str(user.id)


def test_password_exactly_8_chars_is_accepted(client):
    register(client, password="exactly8")
    assert User.query.count() == 1


# --- Duplicate user -----------------------------------------------------------

def test_duplicate_username_is_rejected(client):
    register(client, username="ryan", email="first@example.com")
    response = register(client, username="ryan", email="second@example.com")

    assert response.status_code != 500
    assert User.query.count() == 1
    assert User.query.filter_by(email="second@example.com").first() is None


def test_duplicate_email_is_rejected(client):
    register(client, username="first", email="same@example.com")
    response = register(client, username="second", email="same@example.com")

    assert response.status_code != 500
    assert User.query.count() == 1
    assert User.query.filter_by(username="second").first() is None


# --- Bad input ----------------------------------------------------------------

@pytest.mark.parametrize("username, email, password", [
    ("", "ryan@example.com", PASSWORD),       # missing username
    ("ryan", "", PASSWORD),                   # missing email
    ("ryan", "ryan@example.com", ""),         # missing password
    ("ryan", "ryan@example.com", "short7!"),  # 7 chars, under the 8 minimum
    ("ryan", "not-an-email", PASSWORD),       # invalid email
])
def test_bad_input_creates_no_account(client, username, email, password):
    response = register(client, username=username, email=email, password=password)

    assert response.status_code != 500
    assert response.status_code not in (302, 303), "bad input should not redirect"
    assert User.query.count() == 0


# --- Password is hashed -------------------------------------------------------

def test_password_is_hashed(client):
    register(client)
    user = User.query.filter_by(username="ryan").one()

    assert user.password_hash != PASSWORD
    assert PASSWORD not in user.password_hash
    assert check_password_hash(user.password_hash, PASSWORD)
    assert not check_password_hash(user.password_hash, "wrong-password")


def test_same_password_gets_different_hashes(client):
    register(client, username="a", email="a@example.com")
    register(client, username="b", email="b@example.com")
    a, b = User.query.order_by(User.username).all()

    assert a.password_hash != b.password_hash  # salted
