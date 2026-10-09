"""Tests for NTT-23 (E-01-T3): database models and the `flask init-db` command.

Acceptance criterion covered (from story E-01, NTT-1):
  - `flask init-db` creates the SQLite database with User, Composition, and Note tables.

Also checks the model rules that later stories depend on:
  - usernames and emails are unique (US-01)
  - a composition belongs to a user (US-03)
  - notes come back in position order, and two notes can't share a position (US-04)
  - a rest is a note with no pitch (US-05)
  - deleting a composition deletes its notes (US-09)

These tests build a tiny Flask app here so they only depend on models.py and db_cli.py.
Once the app factory (NTT-22) is merged, the fixtures can switch to create_app().
"""
import pytest
from flask import Flask
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from models import db, User, Composition, Note
from db_cli import register_db_commands


def make_app(database_uri):
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    register_db_commands(app)
    return app


@pytest.fixture
def app():
    """App with an in-memory database and all tables created."""
    app = make_app("sqlite:///:memory:")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def make_user(username="vs", email="vs@example.com"):
    user = User(username=username, email=email, password_hash="hashed-not-plain")
    db.session.add(user)
    db.session.commit()
    return user


def make_composition(user, title="Ode to Joy"):
    comp = Composition(
        owner=user, title=title, key_signature="C major",
        time_signature="4/4", tempo=120,
    )
    db.session.add(comp)
    db.session.commit()
    return comp


# --- Acceptance criterion: flask init-db creates the three tables -------------

def test_init_db_command_creates_tables(tmp_path):
    db_file = tmp_path / "noted.db"
    app = make_app(f"sqlite:///{db_file}")

    result = app.test_cli_runner().invoke(args=["init-db"])

    assert result.exit_code == 0
    assert "Database initialized successfully." in result.output
    assert db_file.exists()
    with app.app_context():
        tables = set(inspect(db.engine).get_table_names())
    assert {"users", "compositions", "notes"} <= tables


# --- Users --------------------------------------------------------------------

def test_create_user(app):
    user = make_user()
    assert User.query.count() == 1
    assert user.id is not None


def test_username_must_be_unique(app):
    make_user(username="vs", email="a@example.com")
    with pytest.raises(IntegrityError):
        make_user(username="vs", email="b@example.com")


def test_email_must_be_unique(app):
    make_user(username="a", email="same@example.com")
    with pytest.raises(IntegrityError):
        make_user(username="b", email="same@example.com")


# --- Compositions -------------------------------------------------------------

def test_composition_belongs_to_user(app):
    user = make_user()
    comp = make_composition(user)
    assert comp.owner is user
    assert user.compositions == [comp]


def test_composition_requires_title(app):
    user = make_user()
    db.session.add(Composition(owner=user, title=None, key_signature="C major",
                               time_signature="4/4", tempo=120))
    with pytest.raises(IntegrityError):
        db.session.commit()


# --- Notes --------------------------------------------------------------------

def test_notes_are_returned_in_position_order(app):
    comp = make_composition(make_user())
    # added out of order on purpose
    for pos, pitch in [(2, "E"), (0, "C"), (1, "D")]:
        db.session.add(Note(composition=comp, position=pos, pitch=pitch,
                            octave=4, duration="quarter"))
    db.session.commit()
    db.session.expire(comp)
    assert [n.pitch for n in comp.notes] == ["C", "D", "E"]


def test_two_notes_cannot_share_a_position(app):
    comp = make_composition(make_user())
    db.session.add(Note(composition=comp, position=0, pitch="C", octave=4, duration="quarter"))
    db.session.add(Note(composition=comp, position=0, pitch="D", octave=4, duration="quarter"))
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_rest_is_a_note_without_pitch(app):
    comp = make_composition(make_user())
    rest = Note(composition=comp, position=0, duration="half", is_rest=True)
    db.session.add(rest)
    db.session.commit()
    assert rest.pitch is None and rest.octave is None
    assert rest.is_rest is True


def test_is_rest_defaults_to_false(app):
    comp = make_composition(make_user())
    note = Note(composition=comp, position=0, pitch="G", octave=4, duration="eighth")
    db.session.add(note)
    db.session.commit()
    assert note.is_rest is False


# --- Deleting -----------------------------------------------------------------

def test_deleting_composition_deletes_its_notes(app):
    comp = make_composition(make_user())
    db.session.add(Note(composition=comp, position=0, pitch="C", octave=4, duration="quarter"))
    db.session.commit()

    db.session.delete(comp)
    db.session.commit()

    assert Composition.query.count() == 0
    assert Note.query.count() == 0


def test_deleting_user_deletes_their_compositions(app):
    user = make_user()
    make_composition(user)

    db.session.delete(user)
    db.session.commit()

    assert Composition.query.count() == 0
