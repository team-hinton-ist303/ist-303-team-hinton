

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


@pytest.fixture
def app():
    """Create a temporary Flask app for testing."""
    test_app = Flask(__name__)

    test_app.config["TESTING"] = True
    test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    @test_app.get("/health")
    def health():
        return {"status": "ok"}

    return test_app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture
def database(app):
    """Provide an isolated in-memory database for testing."""
    test_db = SQLAlchemy()
    test_db.init_app(app)

    with app.app_context():
        yield test_db
        test_db.session.remove()