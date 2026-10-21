
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from models import Composition, Note, User, db


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the SQLite database tables."""
    db.create_all()
    click.echo("Database initialized successfully.")


# ---- Demo data -----------------------------------------------------------

DEMO_USERNAME = "demo"
DEMO_EMAIL = "demo@noted.test"
DEMO_PASSWORD = "noted-demo-2026"

# (title, key, time signature, tempo, notes). Notes are (pitch, octave, duration);
# pitch None means a rest. Both tunes are public domain.
DEMO_PIECES = [
    ("Ode to Joy (opening)", "C major", "4/4", 100, [
        ("E", 4, "quarter"), ("E", 4, "quarter"), ("F", 4, "quarter"), ("G", 4, "quarter"),
        ("G", 4, "quarter"), ("F", 4, "quarter"), ("E", 4, "quarter"), ("D", 4, "quarter"),
        ("C", 4, "quarter"), ("C", 4, "quarter"), ("D", 4, "quarter"), ("E", 4, "quarter"),
        ("E", 4, "quarter"), ("D", 4, "eighth"), ("D", 4, "half"),
    ]),
    ("Twinkle, Twinkle", "C major", "4/4", 90, [
        ("C", 4, "quarter"), ("C", 4, "quarter"), ("G", 4, "quarter"), ("G", 4, "quarter"),
        ("A", 4, "quarter"), ("A", 4, "quarter"), ("G", 4, "half"),
        (None, None, "quarter"),
    ]),
    ("Waltz sketch", "F major", "3/4", 120, []),
]


def seed_demo():
    """Create (or reset) the demo user and their demo pieces. Returns the user."""
    db.create_all()
    user = User.query.filter_by(username=DEMO_USERNAME).first()
    if user is None:
        user = User(username=DEMO_USERNAME, email=DEMO_EMAIL,
                    password_hash=generate_password_hash(DEMO_PASSWORD))
        db.session.add(user)
    else:
        user.password_hash = generate_password_hash(DEMO_PASSWORD)
        for composition in list(user.compositions):
            db.session.delete(composition)  # notes are deleted with it (cascade)
    db.session.flush()

    for title, key, time_signature, tempo, notes in DEMO_PIECES:
        composition = Composition(owner=user, title=title, key_signature=key,
                                  time_signature=time_signature, tempo=tempo)
        for position, (pitch, octave, duration) in enumerate(notes, start=1):
            composition.notes.append(Note(position=position, pitch=pitch, octave=octave,
                                          duration=duration, is_rest=pitch is None))
        db.session.add(composition)

    db.session.commit()
    return user


@click.command("seed-demo")
@with_appcontext
def seed_demo_command():
    """Create a demo user with a few pieces (safe to run again: it resets them)."""
    seed_demo()
    click.echo("Demo data ready.")
    click.echo(f"  Log in with:  {DEMO_USERNAME} / {DEMO_PASSWORD}")
    click.echo(f"  Pieces:       {', '.join(p[0] for p in DEMO_PIECES)}")


def register_db_commands(app):
    """Register database commands with the Flask app."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_demo_command)
