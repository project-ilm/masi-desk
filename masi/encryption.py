# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Authenticated encryption. The public record holds ciphertext, not the review."""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _key(reviewer_key: bytes) -> bytes:
    # A short key padded with zeros is a weak key. Refuse it; a passphrase needs a KDF first.
    if len(reviewer_key) not in (16, 24, 32):
        raise ValueError("an AES-GCM key is 16, 24 or 32 bytes")
    return reviewer_key


def seal(body: bytes, reviewer_key: bytes) -> dict:
    reviewer_key = _key(reviewer_key)
    nonce = os.urandom(12)
    ciphertext = AESGCM(reviewer_key).encrypt(nonce, body, b"masi-review")
    return {
        "scheme": "AES-GCM",
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex(),
        "delivery": "reviewer-key",
    }


def open_seal(packed: dict, reviewer_key: bytes) -> bytes:
    reviewer_key = _key(reviewer_key)
    return AESGCM(reviewer_key).decrypt(
        bytes.fromhex(packed["nonce"]),
        bytes.fromhex(packed["ciphertext"]),
        b"masi-review",
    )
