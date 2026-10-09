import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-before-deployment")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///noted.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False