import hashlib


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_integrity(text: str, expected_hash: str) -> bool:
    return sha256_hex(text) == expected_hash
