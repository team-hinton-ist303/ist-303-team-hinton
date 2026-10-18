import pytest
from werkzeug.security import generate_password_hash

from models import User, db


@pytest.fixture
def registered_user(app):
    user = User(
        username="daniel",
        email="daniel@example.com",
        password_hash=generate_password_hash("test-password"),
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_login_page(client):
    response = client.get("/auth/login")

    assert response.status_code == 200
    assert b'name="username"' in response.data
    assert b'name="password"' in response.data


def test_correct_login(client, registered_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "daniel",
            "password": "test-password",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/library/"

    with client.session_transaction() as session:
        assert session["_user_id"] == str(registered_user.id)

    response = client.get("/library/")
    assert response.status_code == 200
    assert b"My Library" in response.data


@pytest.mark.parametrize(
    "username,password",
    [
        ("daniel", "wrong-password"),
        ("unknown", "test-password"),
        ("", ""),
    ],
)
def test_invalid_login(client, registered_user, username, password):
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

    with client.session_transaction() as session:
        assert "_user_id" not in session


def test_library_requires_login(client):
    response = client.get("/library/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]