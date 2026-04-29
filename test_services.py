"""Service-layer tests — exercise pure logic without HTTP."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("USE_INMEMORY_DB", "true")

import pytest
from backend.database.db import _state
from backend.utils import security
from backend.services import auth_service, vault_service, admin_service
from backend.services.auth_service import AuthError
from backend.services.vault_service import VaultError
from backend.utils.validators import ValidationError


@pytest.fixture(autouse=True)
def _reset(app):  # uses the test app fixture so request context is available
    _state["memory"] = {"users": [], "vault": [], "logs": []}
    security.reset_all()
    with app.test_request_context("/"):
        yield


def test_register_and_login_via_service(app):
    with app.test_request_context("/"):
        out = auth_service.register_user(
            {"username": "carol", "password": "password123", "role": "user"}
        )
        assert out["user"]["username"] == "carol"

        out = auth_service.login_user(
            {"username": "carol", "password": "password123"}, ip="1.2.3.4"
        )
        assert out["token"]


def test_login_invalid_raises(app):
    with app.test_request_context("/"):
        auth_service.register_user(
            {"username": "carol", "password": "password123"}
        )
        with pytest.raises(AuthError) as e:
            auth_service.login_user(
                {"username": "carol", "password": "WRONG"}, ip="1.2.3.4"
            )
        assert e.value.status == 401


def test_register_validation(app):
    with app.test_request_context("/"):
        with pytest.raises(ValidationError):
            auth_service.register_user({"username": "a!", "password": "password123"})


def test_vault_owner_check(app):
    with app.test_request_context("/"):
        u1 = auth_service.register_user(
            {"username": "user1", "password": "password123"}
        )["user"]
        u1_full = {"_id": u1["id"], "username": u1["username"], "role": "user"}
        item = vault_service.create_item(
            u1_full,
            {"name": "X", "formula": "Y", "notes": "secret", "key": "k1"},
        )

        u2 = auth_service.register_user(
            {"username": "user2", "password": "password123"}
        )["user"]
        u2_full = {"_id": u2["id"], "username": u2["username"], "role": "user"}
        with pytest.raises(VaultError) as e:
            vault_service.decrypt_item(u2_full, item["id"], "k1")
        assert e.value.status == 403


def test_admin_stats_shape(app):
    with app.test_request_context("/"):
        auth_service.register_user(
            {"username": "admin1", "password": "password123", "role": "admin"}
        )
        s = admin_service.system_stats()
        assert "totals" in s and "by_event" in s and "by_severity" in s
        assert s["totals"]["users"] >= 1
