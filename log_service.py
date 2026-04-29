"""
Centralised logging service.

All routes/services emit audit events via this module, NOT by calling
`add_log` directly. This keeps log shape consistent and makes it easy to
swap the persistence layer later (file, syslog, ELK, CloudWatch...).
"""
from __future__ import annotations

import logging
from typing import Optional

from flask import has_request_context, request

from backend.database.db import add_log, list_logs

# Mirror events to stdout for `docker logs` / Render / CloudWatch.
_logger = logging.getLogger("dna_vault.audit")
if not _logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(asctime)s] AUDIT %(message)s"))
    _logger.addHandler(h)
    _logger.setLevel(logging.INFO)


def _client_ip() -> str:
    if not has_request_context():
        return "system"
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _ua() -> str:
    if not has_request_context():
        return ""
    return request.headers.get("User-Agent", "")[:200]


def log_event(
    event: str,
    *,
    severity: str = "info",
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    **fields,
) -> dict:
    """
    Persist an audit log entry and mirror it to the application logger.

    severity ∈ {"info", "warning", "critical"}
    """
    entry = {
        "event": event,
        "severity": severity,
        "ip": _client_ip(),
        "ua": _ua(),
        "path": request.path if has_request_context() else None,
    }
    if user_id is not None:
        entry["user_id"] = user_id
    if username is not None:
        entry["username"] = username
    entry.update(fields)
    add_log(entry)
    _logger.info(
        "%s severity=%s user=%s ip=%s extras=%s",
        event, severity, username or user_id or "-", entry["ip"],
        {k: v for k, v in fields.items() if k not in ("password", "key")},
    )
    return entry


# Convenience wrappers — make call sites read like English.
def info(event, **kw): return log_event(event, severity="info", **kw)
def warn(event, **kw): return log_event(event, severity="warning", **kw)
def critical(event, **kw): return log_event(event, severity="critical", **kw)


def fetch_logs(user_id: Optional[str] = None, limit: int = 500):
    return list_logs(user_id=user_id, limit=limit)
