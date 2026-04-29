"""
Brute-force protection: track failed login attempts per username + IP and
lock the combo for a configurable cooldown.
"""
import time
from threading import Lock
from collections import defaultdict

from config import Config

_failures = defaultdict(list)  # key -> [timestamps]
_lock = Lock()


def _key(username: str, ip: str) -> str:
    return f"{(username or '').lower()}|{ip or 'unknown'}"


def _prune(now: float, k: str):
    window = Config.LOGIN_LOCKOUT_SECONDS
    _failures[k] = [t for t in _failures[k] if now - t < window]


def is_locked(username: str, ip: str):
    """Return (locked: bool, retry_after_seconds: int)."""
    now = time.time()
    k = _key(username, ip)
    with _lock:
        _prune(now, k)
        attempts = _failures[k]
        if len(attempts) >= Config.LOGIN_MAX_ATTEMPTS:
            oldest = min(attempts)
            retry = int(Config.LOGIN_LOCKOUT_SECONDS - (now - oldest))
            return True, max(retry, 1)
    return False, 0


def record_failure(username: str, ip: str) -> int:
    now = time.time()
    k = _key(username, ip)
    with _lock:
        _prune(now, k)
        _failures[k].append(now)
        return len(_failures[k])


def reset(username: str, ip: str):
    k = _key(username, ip)
    with _lock:
        _failures.pop(k, None)


def reset_all():
    with _lock:
        _failures.clear()
