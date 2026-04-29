import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("USE_INMEMORY_DB", "true")
os.environ.setdefault("LOGIN_MAX_ATTEMPTS", "3")
os.environ.setdefault("LOGIN_LOCKOUT_SECONDS", "60")
# Disable rate limiting noise during tests
os.environ.setdefault("RATE_LIMIT_DEFAULT", "10000 per minute")
os.environ.setdefault("RATE_LIMIT_AUTH", "10000 per minute")
os.environ.setdefault("RATE_LIMIT_ATTACK", "10000 per minute")


@pytest.fixture()
def app():
    from app import create_app
    from backend.database.db import _state
    from backend.utils import security

    # Reset in-memory state between tests
    _state["memory"] = {"users": [], "vault": [], "logs": []}
    security.reset_all()

    application = create_app({"TESTING": True})
    return application


@pytest.fixture()
def client(app):
    return app.test_client()


def _register(client, username="alice", password="password123", role="user"):
    return client.post("/api/auth/register", json={
        "username": username, "password": password, "role": role,
    })


def _login(client, username="alice", password="password123"):
    return client.post("/api/auth/login", json={
        "username": username, "password": password,
    })


@pytest.fixture()
def user_token(client):
    _register(client, "alice", "password123", "user")
    r = _login(client, "alice", "password123")
    return r.get_json()["token"]


@pytest.fixture()
def admin_token(client):
    _register(client, "root", "password123", "admin")
    r = _login(client, "root", "password123")
    return r.get_json()["token"]


@pytest.fixture()
def auth_header():
    def _h(token):
        return {"Authorization": f"Bearer {token}"}
    return _h
