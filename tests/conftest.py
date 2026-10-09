"""Shared pytest fixtures for Noted!

Every test that uses these fixtures runs against the real app (create_app) and
the real models, with a fresh in-memory SQLite database for each test.
"""
import pytest

from app import create_app
from models import db


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


# TODO (E-01-T4): add a `logged_in_client` fixture once login (US-02) is merged,
# so tests for protected pages can start as a logged-in user.