
import click
from flask.cli import with_appcontext
from models import db


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the SQLite database tables."""
    db.create_all()
    click.echo("Database initialized successfully.")


def register_db_commands(app):
    """Register database commands with the Flask app."""
    app.cli.add_command(init_db_command)
