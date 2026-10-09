
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    compositions = db.relationship(
        "Composition",
        back_populates="owner",
        cascade="all, delete-orphan"
    )


class Composition(db.Model):
    __tablename__ = "compositions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    key_signature = db.Column(db.String(20), nullable=False)
    time_signature = db.Column(db.String(8), nullable=False)
    tempo = db.Column(db.Integer, nullable=False)

    owner = db.relationship(
        "User", back_populates="compositions"
    )

    notes = db.relationship(
        "Note",
        back_populates="composition",
        cascade="all, delete-orphan",
        order_by="Note.position"
    )


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    composition_id = db.Column(
        db.Integer,
        db.ForeignKey("compositions.id"),
        nullable=False
    )
    position = db.Column(db.Integer, nullable=False)
    pitch = db.Column(db.String(1), nullable=True)
    octave = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.String(20), nullable=False)
    accidental = db.Column(db.String(10), nullable=True)
    is_rest = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "composition_id",
            "position",
            name="uq_note_composition_position"
        ),
    )

    composition = db.relationship(
        "Composition", back_populates="notes"
    )
