"""Admin / audit service."""
from __future__ import annotations

from collections import Counter

from backend.database.db import list_users, list_vault
from backend.services import log_service


def all_users():
    return list_users()


def filtered_logs(*, event=None, severity=None, q="", limit=500):
    logs = log_service.fetch_logs(limit=limit)
    if event:
        logs = [l for l in logs if l.get("event") == event]
    if severity:
        logs = [l for l in logs if l.get("severity") == severity]
    if q:
        ql = q.lower()
        logs = [l for l in logs if ql in str(l).lower()]
    return logs


def system_stats():
    logs = log_service.fetch_logs(limit=2000)
    users = list_users()
    vault = list_vault(None)

    by_event = Counter(l.get("event", "unknown") for l in logs)
    by_severity = Counter(l.get("severity", "info") for l in logs)
    failed_logins = sum(1 for l in logs if l.get("event") == "login_failed")
    successful_logins = sum(1 for l in logs if l.get("event") == "login_success")
    attacks = sum(1 for l in logs if str(l.get("event", "")).startswith("attack_"))
    integrity_failures = sum(1 for l in logs if l.get("integrity_ok") is False)
    locked = sum(1 for l in logs if l.get("event") == "login_locked")

    return {
        "totals": {
            "users": len(users),
            "vault_items": len(vault),
            "log_entries": len(logs),
            "failed_logins": failed_logins,
            "successful_logins": successful_logins,
            "attack_simulations": attacks,
            "integrity_failures": integrity_failures,
            "lockouts": locked,
        },
        "by_event": dict(by_event.most_common(20)),
        "by_severity": dict(by_severity),
        "users_by_role": dict(Counter(u.get("role", "user") for u in users)),
    }
