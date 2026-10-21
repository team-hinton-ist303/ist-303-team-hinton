import pytest
from werkzeug.security import generate_password_hash

from models import User, db


@pytest.fixture
def logged_in(client, app):
    user = User(
        username="logout_tester",
        email="logout@example.com",
        password_hash=generate_password_hash("test-password"),
    )
    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/auth/login",
        data={
            "username": "logout_tester",
            "password": "test-password",
        },
    )
    assert response.status_code == 302
    return client


def nav_html(response):
    html = response.get_data(as_text=True)
    return html.split("<nav", 1)[1].split("</nav>", 1)[0]


def test_logged_out_navigation(client):
    nav = nav_html(client.get("/"))

    assert 'href="/auth/login"' in nav
    assert 'href="/auth/register"' in nav
    assert "My Library" not in nav
    assert "Log out" not in nav


def test_logged_in_navigation(logged_in):
    nav = nav_html(logged_in.get("/"))

    assert "logout_tester" in nav
    assert "My Library" in nav
    assert "New piece" in nav
    assert 'action="/auth/logout" method="post"' in nav
    assert "Log out" in nav
    assert 'href="/auth/login"' not in nav
    assert 'href="/auth/register"' not in nav


def test_logout_ends_session_and_returns_home(logged_in):
    response = logged_in.post("/auth/logout")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with logged_in.session_transaction() as session:
        assert "_user_id" not in session

    nav = nav_html(logged_in.get("/"))
    assert 'href="/auth/login"' in nav
    assert 'href="/auth/register"' in nav
    assert "Log out" not in nav

    protected = logged_in.get("/library/")
    assert protected.status_code == 302
    assert "/auth/login" in protected.headers["Location"]


def test_logout_requires_login(client):
    response = client.post("/auth/logout")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_get_does_not_log_user_out(logged_in):
    response = logged_in.get("/auth/logout")

    assert response.status_code == 405

    with logged_in.session_transaction() as session:
        assert "_user_id" in session