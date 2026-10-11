
from sqlalchemy import text


def test_database_connection(database):
    """Verify the in-memory SQLite database works."""
    result = database.session.execute(
        text("SELECT 1")
    ).scalar_one()

    assert result == 1
