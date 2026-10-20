import pytest
from werkzeug.security import generate_password_hash

from models import Composition, User, db


VALID = {
    "title": "  Morning Melody  ",
    "key_signature": "Bb major",
    "time_signature": "3/4",
    "tempo": "120",
}


@pytest.fixture
def users(app):
    password_hash = generate_password_hash("test-password")
    owner = User(
        username="owner",
        email="owner@example.com",
        password_hash=password_hash,
    )
    other = User(
        username="other",
        email="other@example.com",
        password_hash=password_hash,
    )
    db.session.add_all([owner, other])
    db.session.commit()
    return owner.id, other.id


@pytest.fixture
def logged_in(client, users):
    response = client.post(
        "/auth/login",
        data={"username": "owner", "password": "test-password"},
    )
    assert response.status_code == 302
    return client


def test_create_saves_and_redirects_to_editor(logged_in, users):
    owner_id, other_id = users

    response = logged_in.post(
        "/compositions/new",
        data={**VALID, "user_id": str(other_id)},
    )

    assert response.status_code == 302

    
    # Reload stored values from the database.
    db.session.expire_all()
    saved = db.session.execute(
        db.select(Composition)
    ).scalars().all()

    assert len(saved) == 1
    composition = saved[0]
    assert composition.user_id == owner_id
    assert composition.title == "Morning Melody"
    assert composition.key_signature == "Bb major"
    assert composition.time_signature == "3/4"
    assert composition.tempo == 120
    assert response.headers["Location"] == (
        f"/compositions/{composition.id}"
    )

    page = logged_in.get(response.headers["Location"])
    assert page.status_code == 200
    assert b"Morning Melody" in page.data
    assert b"No notes yet." in page.data


@pytest.mark.parametrize(
    "field,bad",
    [
        ("title", "   "),
        ("title", "x" * 201),
        ("key_signature", "H major"),
        ("time_signature", "5/4"),
        ("tempo", "fast"),
        ("tempo", "120.5"),
        ("tempo", "39"),
        ("tempo", "241"),
    ],
)
def test_invalid_submission_saves_nothing(logged_in, field, bad):
    response = logged_in.post(
        "/compositions/new",
        data={**VALID, field: bad},
    )

    assert response.status_code == 400
    assert b"Please fix the highlighted fields" in response.data
    assert db.session.execute(
        db.select(Composition)
    ).scalars().all() == []


def test_logged_out_post_is_blocked(client, app):
    response = client.post("/compositions/new", data=VALID)

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
    assert db.session.execute(
        db.select(Composition)
    ).scalars().all() == []


def test_logged_out_editor_is_blocked(client):
    response = client.get("/compositions/1")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_other_users_composition_is_hidden(logged_in, users):
    _, other_id = users
    composition = Composition(
        user_id=other_id,
        title="Private composition",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )
    db.session.add(composition)
    db.session.commit()

    response = logged_in.get(f"/compositions/{composition.id}")

    assert response.status_code == 404
    assert b"Private composition" not in response.data


def test_missing_composition_returns_404(logged_in):
    assert logged_in.get("/compositions/999999").status_code == 404