# Architecture

## Encryption pipeline

1. **Plaintext** → UTF-8 bytes
2. **Bytes → binary** (8 bits per byte)
3. **Binary pairs (00,01,10,11) → DNA bases**
   - Mapping is one of 24 permutations of A,T,G,C
   - The permutation index is derived from `SHA-256(key)[0] % 24`
4. **Mutation layer**: each base is rotated in the (A,T,G,C) ring by an
   offset derived from a SHA-256 keystream over `(key, counter)`.

Decryption reverses the mutation, then maps DNA back to binary, then bytes.

## Integrity

Before encryption, the plaintext is hashed with SHA-256 and the digest is
stored alongside the ciphertext. On decryption the plaintext is re-hashed
and compared — any mismatch flags tampering.

## Attack model

- **Wrong-key attempt**: a different key produces a different mapping and
  a different mutation stream, so decoded bytes are usually invalid UTF-8
  or random garbage.
- **Tampering**: flipping even one base changes the mutation chain locally
  and breaks the SHA-256 integrity check.
- **Unauthorized**: requests without a valid JWT are rejected at the
  middleware layer and logged.
