"""
DNA Cryptography Engine
-----------------------
Pipeline: text -> bytes -> binary -> DNA(A,T,G,C) -> mutation layer -> ciphertext

Uses a key-derived dynamic mapping of binary pairs to DNA bases, plus a
key-driven mutation (rotation in DNA-base space) for added security.
"""
import hashlib
from itertools import permutations

BASES = ["A", "T", "G", "C"]
COMPLEMENT = {"A": "T", "T": "A", "G": "C", "C": "G"}
BIN_PAIRS = ["00", "01", "10", "11"]
_PERMUTATIONS = list(permutations(BASES))  # 24 possible mappings


def _key_seed(key: str) -> bytes:
    return hashlib.sha256(key.encode("utf-8")).digest()


def _mapping_for_key(key: str):
    seed = _key_seed(key)
    idx = seed[0] % len(_PERMUTATIONS)
    perm = _PERMUTATIONS[idx]
    enc_map = dict(zip(BIN_PAIRS, perm))
    dec_map = {v: k for k, v in enc_map.items()}
    return enc_map, dec_map


def _mutation_stream(key: str, length: int):
    seed = _key_seed(key)
    out = bytearray()
    counter = 0
    while len(out) < length:
        out.extend(hashlib.sha256(seed + counter.to_bytes(4, "big")).digest())
        counter += 1
    return out[:length]


def _mutate(dna: str, key: str, decrypt: bool = False) -> str:
    stream = _mutation_stream(key, len(dna))
    out = []
    for i, base in enumerate(dna):
        offset = stream[i] % 4
        if decrypt:
            offset = (-offset) % 4
        new_idx = (BASES.index(base) + offset) % 4
        out.append(BASES[new_idx])
    return "".join(out)


def encrypt(plaintext: str, key: str) -> str:
    if not key:
        raise ValueError("Encryption key required")
    enc_map, _ = _mapping_for_key(key)
    binary = "".join(f"{b:08b}" for b in plaintext.encode("utf-8"))
    dna = "".join(enc_map[binary[i:i+2]] for i in range(0, len(binary), 2))
    return _mutate(dna, key, decrypt=False)


def decrypt(ciphertext: str, key: str) -> str:
    if not key:
        raise ValueError("Decryption key required")
    if any(c not in BASES for c in ciphertext):
        raise ValueError("Ciphertext contains non-DNA characters")
    _, dec_map = _mapping_for_key(key)
    dna = _mutate(ciphertext, key, decrypt=True)
    binary = "".join(dec_map[b] for b in dna)
    n = len(binary) // 8
    raw = bytes(int(binary[i*8:(i+1)*8], 2) for i in range(n))
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("Decryption failed: invalid key or corrupted data")


def complement_strand(dna: str) -> str:
    """Return the Watson–Crick complement strand for visualization."""
    return "".join(COMPLEMENT.get(b, b) for b in dna)


def encode_visualization(plaintext: str, key: str):
    """Return per-step DNA strands + complement for UI visualization."""
    enc_map, _ = _mapping_for_key(key)
    binary = "".join(f"{b:08b}" for b in plaintext.encode("utf-8"))
    raw_dna = "".join(enc_map[binary[i:i+2]] for i in range(0, len(binary), 2))
    mutated = _mutate(raw_dna, key, decrypt=False)
    return {
        "binary": binary,
        "dna": raw_dna,
        "mutated": mutated,
        "complement": complement_strand(mutated),
        "mapping": enc_map,
    }
