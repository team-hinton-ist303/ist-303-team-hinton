"""Tests for US-03-T4 (NTT-38): creating a composition.

Task: valid create, missing title, tempo out of range, owner is set.

Acceptance criteria covered (from story US-03, NTT-5):
  - Submitting a valid form creates a composition owned by me and opens it in the editor.
  - A blank title or out-of-range tempo shows an error and nothing is saved.
  - The editor shows the title, key, time signature, and tempo I chose.

These go through the real routes (POST /compositions/new, then the editor page).
test_new_composition_form.py already checks the form's options and the validator
on its own; test_create_composition.py has the first route tests (NTT-36).
"""
import re

import pytest
from werkzeug.security import generate_password_hash

from compositions import KEY_SIGNATURES, TEMPO_MAX, TEMPO_MIN, TIME_SIGNATURES
from models import Composition, User, db

NEW_URL = "/compositions/new"
PASSWORD = "test-password"
VALID = {
    "title": "Morning Melody",
    "key_signature": "Bb major",
    "time_signature": "3/4",
    "tempo": "120",
}


def make_user(username):
    user = User(username=username, email=f"{username}@example.com",
                password_hash=generate_password_hash(PASSWORD))
    db.session.add(user)
    db.session.commit()
    return user


def log_in(client, username):
    response = client.post("/auth/login", data={"username": username, "password": PASSWORD})
    assert response.status_code == 302


@pytest.fixture
def owner(app):
    return make_user("owner")


@pytest.fixture
def owner_client(client, owner):
    """A client logged in as `owner`. Can switch to the shared fixture once NTT-111 lands."""
    log_in(client, "owner")
    return client


def saved_compositions():
    db.session.expire_all()
    return db.session.execute(db.select(Composition)).scalars().all()


def create(client, **changes):
    return client.post(NEW_URL, data={**VALID, **changes})


# --- Valid create -------------------------------------------------------------

def test_valid_create_saves_one_composition(owner_client):
    response = create(owner_client)

    assert response.status_code == 302
    assert len(saved_compositions()) == 1


def test_valid_create_opens_the_new_piece_in_the_editor(owner_client):
    response = create(owner_client)
    composition = saved_compositions()[0]

    assert response.headers["Location"] == f"/compositions/{composition.id}"
    assert owner_client.get(response.headers["Location"]).status_code == 200


def test_editor_shows_title_key_time_signature_and_tempo(owner_client):
    response = create(owner_client)
    html = owner_client.get(response.headers["Location"]).get_data(as_text=True)
    header = html.split('class="editor-header"', 1)[1].split("</header>", 1)[0]

    assert "Morning Melody" in header
    assert "Bb major" in header
    assert "3/4" in header
    assert "= 120" in header


@pytest.mark.parametrize("key", [value for value, _ in KEY_SIGNATURES])
def test_every_key_can_be_created(owner_client, key):
    create(owner_client, key_signature=key)
    assert saved_compositions()[0].key_signature == key


@pytest.mark.parametrize("time_signature", TIME_SIGNATURES)
def test_every_time_signature_can_be_created(owner_client, time_signature):
    create(owner_client, time_signature=time_signature)
    assert saved_compositions()[0].time_signature == time_signature


@pytest.mark.parametrize("tempo", [TEMPO_MIN, TEMPO_MAX])
def test_tempo_at_the_limits_is_saved(owner_client, tempo):
    create(owner_client, tempo=str(tempo))
    assert saved_compositions()[0].tempo == tempo


def test_title_is_trimmed(owner_client):
    create(owner_client, title="   Morning Melody   ")
    assert saved_compositions()[0].title == "Morning Melody"


# --- Missing title ------------------------------------------------------------

@pytest.mark.parametrize("title", ["", "   "])
def test_missing_title_shows_error_and_saves_nothing(owner_client, title):
    response = create(owner_client, title=title)
    html = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Please give your piece a title." in html
    assert saved_compositions() == []


def test_title_field_left_out_of_the_form_saves_nothing(owner_client):
    data = {k: v for k, v in VALID.items() if k != "title"}
    response = owner_client.post(NEW_URL, data=data)

    assert response.status_code == 400
    assert saved_compositions() == []


def test_error_keeps_what_the_user_typed(owner_client):
    html = create(owner_client, title="").get_data(as_text=True)

    assert 'value="120"' in html                          # tempo kept
    assert 'value="Bb major" selected' in html            # key kept
    assert re.search(r'value="3/4"\s+checked', html)       # time signature kept


# --- Tempo out of range -------------------------------------------------------

@pytest.mark.parametrize("tempo", [str(TEMPO_MIN - 1), str(TEMPO_MAX + 1), "0", "-100", "1000"])
def test_out_of_range_tempo_shows_error_and_saves_nothing(owner_client, tempo):
    response = create(owner_client, tempo=tempo)
    html = response.get_data(as_text=True)

    assert response.status_code == 400
    assert f"Tempo must be between {TEMPO_MIN} and {TEMPO_MAX} BPM." in html
    assert saved_compositions() == []


@pytest.mark.parametrize("tempo", ["", "fast", "120.5"])
def test_non_number_tempo_shows_error_and_saves_nothing(owner_client, tempo):
    response = create(owner_client, tempo=tempo)

    assert response.status_code == 400
    assert "Tempo must be a whole number" in response.get_data(as_text=True)
    assert saved_compositions() == []


def test_blank_title_and_bad_tempo_show_both_errors(owner_client):
    html = create(owner_client, title="", tempo="999").get_data(as_text=True)

    assert "Please give your piece a title." in html
    assert "Tempo must be between" in html
    assert saved_compositions() == []


# --- Owner is set -------------------------------------------------------------

def test_owner_is_the_logged_in_user(owner_client, owner):
    create(owner_client)
    assert saved_compositions()[0].user_id == owner.id


def test_owner_cannot_be_set_from_the_form(owner_client, owner):
    other = make_user("other")
    create(owner_client, user_id=str(other.id), owner=str(other.id))

    assert saved_compositions()[0].user_id == owner.id


def test_each_user_owns_their_own_piece(client, owner):
    # One user at a time: conftest keeps one app context open per test, so
    # Flask-Login's cached user would carry over between two separate clients.
    make_user("other")
    log_in(client, "owner")
    create(client, title="Owner's piece")
    client.post("/auth/logout")
    log_in(client, "other")
    create(client, title="Other's piece")

    owners = {c.title: c.owner.username for c in saved_compositions()}
    assert owners == {"Owner's piece": "owner", "Other's piece": "other"}


def test_new_piece_shows_up_in_my_library(owner_client):
    create(owner_client)
    assert "Morning Melody" in owner_client.get("/library/").get_data(as_text=True)


def test_logged_out_user_cannot_create(client):
    response = create(client)

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
    assert saved_compositions() == []
