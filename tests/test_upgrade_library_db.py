"""Tests for the `upgrade-library-db` command (PR #26, NTT-57).

#26 adds `Composition.updated_at`. `init-db` can't add a column to an existing
table, so `flask --app app upgrade-library-db` adds it to databases created
before #26. These tests build an old-style database and run the command on it.
"""
import sqlite3

import pytest

from app import create_app

OLD_SCHEMA = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);
CREATE TABLE compositions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    key_signature VARCHAR(20) NOT NULL,
    time_signature VARCHAR(8) NOT NULL,
    tempo INTEGER NOT NULL
);
INSERT INTO users (id, username, email, password_hash)
    VALUES (1, 'old_user', 'old@example.com', 'x');
INSERT INTO compositions (id, user_id, title, key_signature, time_signature, tempo)
    VALUES (1, 1, 'Made before #26', 'C major', '4/4', 100);
"""


@pytest.fixture
def old_db_app(tmp_path):
    """An app pointing at a SQLite file created with the pre-#26 schema."""
    path = tmp_path / "old.db"
    with sqlite3.connect(path) as conn:
        conn.executescript(OLD_SCHEMA)
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test-key",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{path}",
    }), path


def columns(path):
    with sqlite3.connect(path) as conn:
        return [row[1] for row in conn.execute("PRAGMA table_info(compositions)")]


def test_upgrade_adds_updated_at_and_keeps_existing_pieces(old_db_app):
    app, path = old_db_app
    assert "updated_at" not in columns(path)

    result = app.test_cli_runner().invoke(args=["upgrade-library-db"])

    assert result.exit_code == 0, result.output
    assert "updated_at" in columns(path)
    with sqlite3.connect(path) as conn:
        title, updated_at = conn.execute(
            "SELECT title, updated_at FROM compositions WHERE id = 1"
        ).fetchone()
    assert title == "Made before #26"
    assert updated_at  # existing rows get a timestamp, not NULL


def test_running_upgrade_twice_is_harmless(old_db_app):
    app, _ = old_db_app
    runner = app.test_cli_runner()
    runner.invoke(args=["upgrade-library-db"])

    result = runner.invoke(args=["upgrade-library-db"])

    assert result.exit_code == 0, result.output
    assert "already up to date" in result.output


def test_library_query_works_after_upgrade(old_db_app):
    """The sort My Library uses (newest edit first) runs on an upgraded database."""
    from models import Composition, db

    app, _ = old_db_app
    app.test_cli_runner().invoke(args=["upgrade-library-db"])

    with app.app_context():
        pieces = db.session.execute(
            db.select(Composition).order_by(Composition.updated_at.desc())
        ).scalars().all()
    assert [p.title for p in pieces] == ["Made before #26"]
