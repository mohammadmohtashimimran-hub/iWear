"""Pytest fixtures for Flask app and DB."""
import pytest
from app import create_app
from app.config import Config
from app.extensions import db as _db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret"
    SECRET_KEY = "test-secret"


@pytest.fixture(scope="session")
def app():
    return create_app(TestConfig)


@pytest.fixture(scope="function")
def client(app, db):
    with app.test_client() as c:
        yield c


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()
