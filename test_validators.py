"""Tests for input validators."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.utils.validators import (
    validate_username, validate_password, validate_role,
    require_str, ValidationError,
)


def test_username_ok():
    assert validate_username("alice_01") == "alice_01"


@pytest.mark.parametrize("bad", ["ab", "x" * 33, "no spaces", "weird!", 123, None])
def test_username_bad(bad):
    with pytest.raises(ValidationError):
        validate_username(bad)


def test_password_min_length():
    with pytest.raises(ValidationError):
        validate_password("short")
    assert validate_password("longenough") == "longenough"


def test_role_default_user():
    assert validate_role(None) == "user"
    assert validate_role("admin") == "admin"
    with pytest.raises(ValidationError):
        validate_role("superuser")


def test_require_str_trims():
    assert require_str("  hi  ", "x") == "hi"
    with pytest.raises(ValidationError):
        require_str("", "x")
    with pytest.raises(ValidationError):
        require_str("a" * 5, "x", min_len=10)
