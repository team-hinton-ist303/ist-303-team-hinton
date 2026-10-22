"""Tests for US-02-T4 (NTT-33): @login_required on all composition and library routes.

Acceptance criterion covered (from story US-02, NTT-4):
  - Visiting a protected page while logged out redirects to the login page.

The main test finds every route in the `compositions` and `library` blueprints
automatically, so any route added later is checked too. If someone adds a new
composition or library page without @login_required, these tests fail.

Uses the shared `client` fixture from conftest.py and a local `logged_in_client`
fixture (can switch to the shared one once NTT-111 lands).
"""
import pytest
from flask import url_for
from werkzeug.security import generate_password_hash

from models import User, db

PROTECTED_BLUEPRINTS = ("compositions", "library")
PUBLIC_PAGES = ["/", "/health", "/auth/login", "/auth/register"]


@pytest.fixture
def logged_in_client(client):
    """A client logged in as user "tester". Can switch to the shared fixture once NTT-111 lands."""
    db.session.add(User(
        username="tester",
        email="tester@example.com",
        password_hash=generate_password_hash("test-password"),
    ))
    db.session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "tester", "password": "test-password"},
    )
    assert response.status_code == 302
    return client


def protected_requests(app):
    """(method, url) for every route in the protected blueprints.

    Routes with URL parts like <int:composition_id> get a placeholder value of 1.
    """
    requests = []
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            if rule.endpoint.split(".")[0] not in PROTECTED_BLUEPRINTS:
                continue
            url = url_for(rule.endpoint, **{arg: 1 for arg in rule.arguments})
            for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
                requests.append((method, url))
    return requests


def assert_redirects_to_login(response, url):
    assert response.status_code == 302, f"{url} should redirect when logged out"
    location = response.headers["Location"]
    assert location.startswith("/auth/login"), f"{url} redirected to {location}"
    return location


# --- Logged out: every protected route redirects to login ---------------------

def test_protected_routes_exist(app):
    """Guards against the route search silently finding nothing."""
    urls = {url for _, url in protected_requests(app)}
    assert "/library/" in urls
    assert any(url.startswith("/compositions/") for url in urls)


def test_every_protected_route_redirects_to_login(app, client):
    for method, url in protected_requests(app):
        response = client.open(url, method=method)
        assert_redirects_to_login(response, f"{method} {url}")


def test_redirect_remembers_requested_page(client):
    location = assert_redirects_to_login(client.get("/library/"), "/library/")
    assert "next=" in location and "library" in location


def test_logged_out_request_does_not_render_page(client):
    response = client.get("/library/")
    assert "My Library" not in response.get_data(as_text=True)


# --- Logged in: protected pages open normally ---------------------------------

@pytest.mark.parametrize("url", ["/library/", "/compositions/preview"])
def test_logged_in_user_can_open_protected_page(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 200


# --- Public pages stay public -------------------------------------------------

@pytest.mark.parametrize("url", PUBLIC_PAGES)
def test_public_pages_do_not_require_login(client, url):
    assert client.get(url).status_code == 200
