import pytest
from flask_login import current_user

from auth import load_user, login_manager
from models import User, db


def test_login_manager_configured(app):
    assert app.login_manager is login_manager
    assert login_manager.login_view == "auth.login"


@pytest.mark.parametrize("user_id", [None, "invalid", "999999"])
def test_unknown_user_returns_none(app, user_id):
    assert load_user(user_id) is None


def test_session_restores_user(app, client):
    user = User(
        username="daniel",
        email="daniel@example.com",
        password_hash="unused-in-this-test",
    )
    db.session.add(user)
    db.session.commit()
    user_id = user.id

    @app.get("/test-current-user")
    def test_current_user():
        return {
            "authenticated": current_user.is_authenticated,
            "id": current_user.get_id(),
            "username": current_user.username,
        }

    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True

    response = client.get("/test-current-user")

    assert response.status_code == 200
    assert response.get_json() == {
        "authenticated": True,
        "id": str(user_id),
        "username": "daniel",
    }