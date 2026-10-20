"""Tests for US-03-T1 (NTT-35): new-composition form."""
import re

import pytest
from werkzeug.security import generate_password_hash

from compositions import (KEY_SIGNATURES, TEMPO_MAX, TEMPO_MIN, TIME_SIGNATURES,
                          render_new_form, validate_new_composition)
from models import User, db

NEW_URL = "/compositions/new"


@pytest.fixture
def logged_in(client, app):
    db.session.add(User(username="vs", email="vs@example.com",
                        password_hash=generate_password_hash("test-password")))
    db.session.commit()
    client.post("/auth/login", data={"username": "vs", "password": "test-password"})
    return client


@pytest.fixture
def html(logged_in):
    response = logged_in.get(NEW_URL)
    assert response.status_code == 200
    return response.get_data(as_text=True)


# ---- page --------------------------------------------------------------

def test_logged_out_user_is_sent_to_login(client):
    response = client.get(NEW_URL)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_form_uses_base_layout_and_posts_to_itself(html):
    assert "<title>New piece · Noted!</title>" in html
    assert 'method="post" action="/compositions/new"' in html


def test_form_field_names_match_composition_model(html):
    for field in ["title", "key_signature", "time_signature", "tempo"]:
        assert f'name="{field}"' in html


def test_form_offers_all_15_major_keys(html):
    assert len(KEY_SIGNATURES) == 15
    for value, _ in KEY_SIGNATURES:
        assert f'value="{value}"' in html


def test_form_offers_the_four_time_signatures(html):
    assert TIME_SIGNATURES == ["2/4", "3/4", "4/4", "6/8"]
    for ts in TIME_SIGNATURES:
        assert f'value="{ts}"' in html


def test_tempo_input_limits(html):
    assert f'min="{TEMPO_MIN}" max="{TEMPO_MAX}"' in html
    assert (TEMPO_MIN, TEMPO_MAX) == (40, 240)


def test_sensible_defaults(html):
    assert 'value="C major" selected' in html
    assert re.search(r'value="4/4"\s+checked', html)
    assert 'value="100"' in html


def test_nav_new_piece_link_points_here(html):
    assert 'href="/compositions/new"' in html


def test_form_shows_errors_and_keeps_values(app):
    with app.test_request_context("/"):
        body, status = render_new_form({"title": "", "tempo": "999"},
                                       {"title": "Please give your piece a title.",
                                        "tempo": "Tempo must be between 40 and 240 BPM."}, 400)
    assert status == 400
    assert "Please give your piece a title." in body
    assert "Tempo must be between 40 and 240 BPM." in body
    assert 'value="999"' in body
    assert 'aria-invalid="true"' in body


# ---- validation helper (for NTT-36) -------------------------------------

VALID = {"title": "  Morning Melody ", "key_signature": "Bb major", "time_signature": "3/4", "tempo": "120"}


def test_valid_form_is_cleaned():
    values, errors = validate_new_composition(VALID)
    assert errors == {}
    assert values == {"title": "Morning Melody", "key_signature": "Bb major",
                      "time_signature": "3/4", "tempo": 120}


@pytest.mark.parametrize("field, bad", [
    ("title", ""),
    ("title", "   "),
    ("title", "x" * 201),
    ("key_signature", "H major"),
    ("time_signature", "5/4"),
    ("tempo", "39"),
    ("tempo", "241"),
    ("tempo", "fast"),
    ("tempo", ""),
])
def test_invalid_field_is_reported(field, bad):
    _, errors = validate_new_composition({**VALID, field: bad})
    assert list(errors) == [field]


@pytest.mark.parametrize("tempo", ["40", "240"])
def test_tempo_bounds_are_inclusive(tempo):
    _, errors = validate_new_composition({**VALID, "tempo": tempo})
    assert errors == {}
