from app import create_app
from models import db
from sqlalchemy import inspect


def make_test_app():
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })


def test_config_and_blueprints():
    app = make_test_app()

    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test-key"
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert {"auth", "compositions", "library"} <= set(app.blueprints)


def test_health():
    response = make_test_app().test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_init_db():
    app = make_test_app()
    result = app.test_cli_runner().invoke(args=["init-db"])

    assert result.exit_code == 0, result.output

    with app.app_context():
        assert {"users", "compositions", "notes"} <= set(
            inspect(db.engine).get_table_names()
        )
        db.session.remove()
        db.drop_all()