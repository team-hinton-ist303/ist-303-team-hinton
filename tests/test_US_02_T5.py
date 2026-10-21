
from werkzeug.security import generate_password_hash
from models import User, db


def test_full_login_logout_flow(client, app):
    # Create a test user
    user = User(
        username="test_student",
        email="test_student@example.com",
        password_hash=generate_password_hash("test-password")
    )
    db.session.add(user)
    db.session.commit()

    # 1. Protected page redirects when logged out
    response = client.get("/library/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

    # 2. Login with a wrong password
    response = client.post(
        "/auth/login",
        data={
            "username": "test_student",
            "password": "wrong-password"
        }
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

    with client.session_transaction() as session:
        assert "_user_id" not in session

    # 3. Login with the correct password
    response = client.post(
        "/auth/login",
        data={
            "username": "test_student",
            "password": "test-password"
        }
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/library/"

    # User can now access the protected page
    response = client.get("/library/")
    assert response.status_code == 200

    # 4. Log out
    response = client.post("/auth/logout")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # User should no longer be authenticated
    with client.session_transaction() as session:
        assert "_user_id" not in session

    # Protected page redirects again after logout
    response = client.get("/library/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
