"""Tests for the `flask seed-demo` command used for the Part B demo."""
from werkzeug.security import check_password_hash

from db_cli import DEMO_PASSWORD, DEMO_PIECES, DEMO_USERNAME
from models import Composition, Note, User


def seed(runner):
    result = runner.invoke(args=["seed-demo"])
    assert result.exit_code == 0, result.output
    return result


def test_seed_creates_demo_user_with_hashed_password(runner):
    result = seed(runner)
    user = User.query.filter_by(username=DEMO_USERNAME).one()
    assert user.password_hash != DEMO_PASSWORD
    assert check_password_hash(user.password_hash, DEMO_PASSWORD)
    assert DEMO_PASSWORD in result.output


def test_seed_creates_pieces_and_notes(runner):
    seed(runner)
    titles = {c.title for c in Composition.query.all()}
    assert titles == {p[0] for p in DEMO_PIECES}
    assert Note.query.count() == sum(len(p[4]) for p in DEMO_PIECES)
    assert Note.query.filter_by(is_rest=True).count() == 1


def test_seed_twice_does_not_duplicate(runner):
    seed(runner)
    seed(runner)
    assert User.query.filter_by(username=DEMO_USERNAME).count() == 1
    assert Composition.query.count() == len(DEMO_PIECES)


def test_seed_resets_pieces_changed_during_a_rehearsal(runner, database):
    seed(runner)
    Composition.query.filter_by(title="Waltz sketch").one().title = "Renamed"
    database.session.commit()
    seed(runner)
    assert {c.title for c in Composition.query.all()} == {p[0] for p in DEMO_PIECES}


def test_demo_user_can_log_in(runner, client):
    seed(runner)
    response = client.post("/auth/login", data={"username": DEMO_USERNAME, "password": DEMO_PASSWORD})
    assert response.status_code == 302
    assert response.headers["Location"] == "/library/"


def test_demo_library_lists_seeded_pieces(runner, client):
    seed(runner)
    client.post("/auth/login", data={"username": DEMO_USERNAME, "password": DEMO_PASSWORD})
    html = client.get("/library/").get_data(as_text=True)
    for title, *_ in DEMO_PIECES:
        assert title in html
