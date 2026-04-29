"""
Vault service — encrypt/decrypt/CRUD for chemical entries.
"""
from __future__ import annotations

from backend.utils.dna_crypto import encrypt, decrypt, encode_visualization
from backend.utils.integrity import sha256_hex, verify_integrity
from backend.utils.validators import require_str, ValidationError
from backend.database.db import (
    insert_vault, list_vault, get_vault, delete_vault,
)
from backend.services import log_service


class VaultError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def _public_item(item: dict) -> dict:
    return {
        "id": item["_id"],
        "user_id": item["user_id"],
        "owner_username": item.get("owner_username"),
        "name": item["name"],
        "formula": item["formula"],
        "encrypted_notes": item["encrypted_notes"],
        "integrity_hash": item["integrity_hash"],
        "created_at": item.get("created_at"),
    }


def create_item(user: dict, payload: dict) -> dict:
    name = require_str(payload.get("name"), "name", max_len=200)
    formula = require_str(payload.get("formula"), "formula", max_len=200)
    notes = payload.get("notes") or ""
    if not isinstance(notes, str) or len(notes) > 10000:
        raise ValidationError("notes must be a string up to 10000 chars")
    key = require_str(payload.get("key"), "key", max_len=200)

    encrypted_notes = encrypt(notes, key)
    integrity_hash = sha256_hex(notes)

    item = insert_vault({
        "user_id": user["_id"],
        "owner_username": user["username"],
        "name": name,
        "formula": formula,
        "encrypted_notes": encrypted_notes,
        "integrity_hash": integrity_hash,
    })
    log_service.info(
        "vault_create",
        user_id=user["_id"], username=user["username"],
        item_id=item["_id"], name=name,
    )
    return _public_item(item)


def list_items(user: dict) -> list[dict]:
    items = list_vault(None if user.get("role") == "admin" else user["_id"])
    return [_public_item(i) for i in items]


def _check_owner_or_admin(item, user):
    if user.get("role") != "admin" and item["user_id"] != user["_id"]:
        log_service.warn(
            "vault_access_denied",
            user_id=user["_id"], item_id=item["_id"],
        )
        raise VaultError("Forbidden", status=403)


def decrypt_item(user: dict, item_id: str, key: str) -> dict:
    item = get_vault(item_id)
    if not item:
        raise VaultError("Not found", status=404)
    _check_owner_or_admin(item, user)

    if not key:
        raise ValidationError("key is required")
    try:
        plaintext = decrypt(item["encrypted_notes"], key)
    except Exception:
        log_service.warn(
            "decrypt_failed", user_id=user["_id"], item_id=item_id,
        )
        raise VaultError(
            "Decryption failed: wrong key or tampered data", status=400,
        )

    integrity_ok = verify_integrity(plaintext, item["integrity_hash"])
    log_service.log_event(
        "vault_decrypt",
        severity="info" if integrity_ok else "critical",
        user_id=user["_id"], item_id=item_id, integrity_ok=integrity_ok,
    )
    return {
        "id": item["_id"],
        "name": item["name"],
        "formula": item["formula"],
        "notes": plaintext,
        "integrity_ok": integrity_ok,
    }


def remove_item(user: dict, item_id: str) -> None:
    item = get_vault(item_id)
    if not item:
        raise VaultError("Not found", status=404)
    _check_owner_or_admin(item, user)
    delete_vault(item_id)
    log_service.info("vault_delete", user_id=user["_id"], item_id=item_id)


def visualize(text: str, key: str) -> dict:
    if not text or not key:
        raise ValidationError("text and key are required")
    if len(text) > 2000:
        text = text[:2000]
    return encode_visualization(text, key)
