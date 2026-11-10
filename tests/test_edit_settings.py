
def test_settings_routes(app):
    routes = {
        rule.endpoint: rule
        for rule in app.url_map.iter_rules()
    }

    get_route = routes["compositions.edit_settings"]
    post_route = routes["compositions.update_settings"]

    expected_url = "/compositions/<int:composition_id>/settings"

    assert get_route.rule == expected_url
    assert post_route.rule == expected_url

    assert "GET" in get_route.methods
    assert "POST" in post_route.methods


def test_edit_settings_prefills_existing_values(app, logged_in_client):
    from compositions import Composition, NEW_FORM_DEFAULTS

    original = {
        **NEW_FORM_DEFAULTS,
        "title": "Original Test Piece",
        "tempo": "132",
    }

    response = logged_in_client.post(
        "/compositions/new",
        data=original,
    )
    assert response.status_code in (302, 303)

    with app.app_context():
        piece = Composition.query.filter_by(
            title="Original Test Piece"
        ).first()

        assert piece is not None
        composition_id = piece.id

    response = logged_in_client.get(
        f"/compositions/{composition_id}/settings"
    )

    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert 'value="Original Test Piece"' in html
    assert 'value="132"' in html

    assert (
        f'value="{original["key_signature"]}" selected'
        in html
    )

    assert f'value="{original["time_signature"]}"' in html
    assert "checked" in html

def test_update_settings_saves_changes(app, logged_in_client):
    from compositions import Composition, NEW_FORM_DEFAULTS

    # Create a piece
    original = {
        **NEW_FORM_DEFAULTS,
        "title": "Before Edit",
        "tempo": "100",
    }

    response = logged_in_client.post(
        "/compositions/new",
        data=original,
    )
    assert response.status_code == 302

    with app.app_context():
        piece = Composition.query.filter_by(
            title="Before Edit"
        ).first()

        assert piece is not None
        piece_id = piece.id

    # Update the piece settings
    updated = {
        **original,
        "title": "After Edit",
        "tempo": "120",
    }

    response = logged_in_client.post(
        f"/compositions/{piece_id}/settings",
        data=updated,
    )

    # Should redirect to the editor
    assert response.status_code == 302

    # Check that changes were saved to the database
    with app.app_context():
        piece = Composition.query.filter_by(id=piece_id).first()

        assert piece.title == "After Edit"
        assert piece.tempo == 120

def test_update_settings_rejects_invalid_tempo(app, logged_in_client):
    from compositions import Composition, NEW_FORM_DEFAULTS

    # Create a piece with valid settings
    original = {
        **NEW_FORM_DEFAULTS,
        "title": "Original Piece",
        "tempo": "100",
    }

    response = logged_in_client.post(
        "/compositions/new",
        data=original,
    )
    assert response.status_code == 302

    with app.app_context():
        piece = Composition.query.filter_by(
            title="Original Piece"
        ).first()

        assert piece is not None
        piece_id = piece.id

    # Submit invalid settings
    invalid = {
        **original,
        "title": "Should Not Save",
        "tempo": "9999",
    }

    response = logged_in_client.post(
        f"/compositions/{piece_id}/settings",
        data=invalid,
    )

    print("HTTP status:", response.status_code)
    print("Tempo error shown:", "Tempo must be between" in response.get_data(as_text=True))

    assert response.status_code == 400

    html = response.get_data(as_text=True)

    # The form should show the error and keep entered values
    assert "Please fix" in html
    assert 'value="Should Not Save"' in html
    assert 'value="9999"' in html

    # The database must keep the original values
    with app.app_context():
        piece = Composition.query.filter_by(id=piece_id).first()

        assert piece.title == "Original Piece"
        assert piece.tempo == 100

def test_settings_missing_piece_returns_404(logged_in_client):
    missing_id = 999999999
    url = f"/compositions/{missing_id}/settings"

    # GET: Cannot open settings for a missing piece
    response = logged_in_client.get(url)
    assert response.status_code == 404

    # POST: Cannot update a missing piece
    response = logged_in_client.post(
        url,
        data={"title": "Should Not Save"},
    )
    assert response.status_code == 404