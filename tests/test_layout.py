"""Tests for E-01-T5 (NTT-25): base layout with nav bar, flash messages and CSS."""
from flask import flash, redirect


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Write music one note at a time." in response.data


def test_home_page_uses_base_layout(client):
    html = client.get("/").get_data(as_text=True)
    assert "<nav" in html
    assert "Noted" in html
    assert "/static/css/style.css" in html
    assert "<title>Noted!</title>" in html


def test_nav_shows_login_and_register_when_logged_out(client):
    html = client.get("/").get_data(as_text=True)
    assert 'href="/auth/login"' in html
    assert 'href="/auth/register"' in html
    assert "Log out" not in html


def test_stylesheet_is_served(client):
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert b"--accent" in response.data
    response.close()


def test_flash_messages_are_shown(app, client):
    def save():
        flash("Composition saved.", "success")
        return redirect("/")

    app.add_url_rule("/_test-flash", "test_flash", save)

    html = client.get("/_test-flash", follow_redirects=True).get_data(as_text=True)
    assert "Composition saved." in html
    assert "flash-success" in html


def test_flash_message_only_shows_once(app, client):
    def save():
        flash("Only once.")
        return redirect("/")

    app.add_url_rule("/_test-flash-once", "test_flash_once", save)

    client.get("/_test-flash-once", follow_redirects=True)
    assert b"Only once." not in client.get("/").data
