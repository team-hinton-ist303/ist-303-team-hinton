"""Shared pytest fixtures for Noted!

Every test that uses these fixtures runs against the real app (create_app) and
the real models, with a fresh in-memory SQLite database for each test.
"""
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from models import User, db


TEST_CONFIG = {
    "TESTING": True,
    "SECRET_KEY": "test-key",
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
}


@pytest.fixture
def app():
    """The Noted! app with an empty in-memory database and all tables created."""
    app = create_app(TEST_CONFIG)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for making requests, e.g. client.get("/health")."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A CLI runner for testing commands, e.g. runner.invoke(args=["init-db"])."""
    return app.test_cli_runner()


@pytest.fixture
def database(app):
    """The app's database (models.db), with tables created and an app context active."""
    return db


# ---- Logged-in user (NTT-111) ---------------------------------------------

TEST_USERNAME = "tester"
TEST_EMAIL = "tester@example.com"
TEST_PASSWORD = "test-password"


@pytest.fixture
def test_user(app):
    """A saved user ("tester"). Use it to create compositions the logged-in user owns."""
    user = User(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        password_hash=generate_password_hash(TEST_PASSWORD),
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def logged_in_client(client, test_user):
    """A test client already logged in as `test_user`, through the real login route.

    Example:
        def test_library_loads(logged_in_client):
            assert logged_in_client.get("/library/").status_code == 200
    """
    response = client.post(
        "/auth/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    assert response.status_code == 302, "logging in the test user failed"
    return client