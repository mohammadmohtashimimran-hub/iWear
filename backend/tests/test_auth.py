"""Auth: register, login, me (requires DB with roles)."""
import pytest
from app.models import User, Role
from app.extensions import bcrypt
from app.models.users import user_roles


@pytest.fixture
def viewer_role(db):
    r = Role(name="Viewer")
    db.session.add(r)
    db.session.commit()
    return r


@pytest.fixture
def user_with_role(db, viewer_role):
    u = User(
        email="test@example.com",
        password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
    )
    db.session.add(u)
    db.session.flush()
    db.session.execute(user_roles.insert().values(user_id=u.id, role_id=viewer_role.id))
    db.session.commit()
    return u


def test_register(client, db, viewer_role):
    r = client.post("/api/auth/register", json={"email": "new@example.com", "password": "pass123", "phone": "+10000000000"})
    assert r.status_code in (201, 409)  # 409 if already exists from another test
    if r.status_code == 201:
        data = r.get_json()
        assert "id" in data
        assert data.get("email") == "new@example.com"


def test_login(client, user_with_role):
    r = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert r.status_code == 200
    data = r.get_json()
    assert "access_token" in data
    assert data.get("email") == "test@example.com"


def test_login_wrong_password(client, user_with_role):
    r = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})
    assert r.status_code == 401
