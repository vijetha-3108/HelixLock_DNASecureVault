"""Unit tests for the DNA crypto engine."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from backend.utils.dna_crypto import (
    encrypt, decrypt, encode_visualization, complement_strand, BASES,
)
from backend.utils.integrity import sha256_hex, verify_integrity


def test_roundtrip_ascii():
    msg = "Highly sensitive: H2SO4 + NaOH -> Na2SO4 + H2O"
    key = "molecule-2025"
    ct = encrypt(msg, key)
    assert set(ct) <= set(BASES)
    assert decrypt(ct, key) == msg


def test_roundtrip_unicode():
    msg = "🧬 αβγ — bond breaks at 250°C"
    ct = encrypt(msg, "k")
    assert decrypt(ct, "k") == msg


def test_wrong_key_does_not_recover_plaintext():
    ct = encrypt("secret", "right-key")
    try:
        out = decrypt(ct, "wrong-key")
        assert out != "secret"
    except ValueError:
        pass


def test_empty_key_rejected():
    with pytest.raises(ValueError):
        encrypt("x", "")
    with pytest.raises(ValueError):
        decrypt("ATGC", "")


def test_non_dna_ciphertext_rejected():
    with pytest.raises(ValueError):
        decrypt("HELLO", "k")


def test_integrity_hash():
    h = sha256_hex("data")
    assert verify_integrity("data", h)
    assert not verify_integrity("data2", h)


def test_visualization_shape():
    v = encode_visualization("hi", "k")
    assert set(v["dna"]) <= set(BASES)
    assert set(v["mutated"]) <= set(BASES)
    assert len(v["complement"]) == len(v["mutated"])
    assert len(v["mapping"]) == 4


def test_complement_pairs():
    assert complement_strand("ATGC") == "TACG"
