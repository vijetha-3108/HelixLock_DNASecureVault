"""
Attack-simulation service: wrong-key, tamper, unauthorized.
"""
from __future__ import annotations

from backend.utils.dna_crypto import decrypt
from backend.utils.integrity import verify_integrity
from backend.database.db import get_vault
from backend.services import log_service


class AttackError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def wrong_key_attack(user: dict, item_id: str, wrong_key: str) -> dict:
    item = get_vault(item_id)
    if not item:
        raise AttackError("Not found", status=404)
    try:
        leaked = decrypt(item["encrypted_notes"], wrong_key or "attacker-guess")
        result = {"status": "decoded_garbage", "output": leaked[:200]}
    except Exception as e:
        result = {"status": "rejected", "reason": str(e)}
    log_service.warn(
        "attack_wrong_key",
        user_id=user["_id"], item_id=item_id, result=result["status"],
    )
    return result


def tamper_attack(user: dict, item_id: str, key: str) -> dict:
    item = get_vault(item_id)
    if not item:
        raise AttackError("Not found", status=404)
    cipher = item["encrypted_notes"]
    if len(cipher) < 2:
        raise AttackError("Ciphertext too short to tamper", status=400)
    flipped = ("T" if cipher[0] != "T" else "A") + cipher[1:]
    try:
        plain = decrypt(flipped, key)
        ok = verify_integrity(plain, item["integrity_hash"])
    except Exception:
        plain, ok = None, False

    log_service.log_event(
        "attack_tamper",
        severity="critical" if not ok else "info",
        user_id=user["_id"], item_id=item_id, integrity_ok=ok,
    )
    return {
        "tampered_cipher_preview": flipped[:60] + ("..." if len(flipped) > 60 else ""),
        "decrypted": plain,
        "integrity_ok": ok,
        "verdict": "TAMPERING DETECTED" if not ok else "no anomaly",
    }


def unauthorized_attack() -> dict:
    log_service.warn("attack_unauthorized")
    return {
        "status": "blocked",
        "message": "Request rejected: no valid JWT token provided.",
    }
