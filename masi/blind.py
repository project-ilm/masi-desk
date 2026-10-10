# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Blind arrival is a setting. The default enables none of the four paths."""

from __future__ import annotations

import hashlib
import hmac

from .store import Refused


def salted_hash(identifier: str, salt: str) -> str:
    return hmac.new(salt.encode(), identifier.encode(), hashlib.sha256).hexdigest()


def apply(policy: dict, identifier: str, salt: str | None) -> dict:
    arrival = policy.get("blind_arrival") or {}
    enabled = [name for name, on in arrival.items() if on]
    if not policy.get("blind"):
        return {"mode": "open", "public": identifier}
    if not enabled:
        raise Refused("blind is on and no arrival path is enabled")
    public = {}
    if arrival.get("salted_issue"):
        if not salt:
            raise Refused("salted issue needs a salt, and the salt is not public")
        public["salted_hash"] = salted_hash(identifier, salt)
    if arrival.get("ciphertext"):
        public["ciphertext"] = True
    if arrival.get("private_review_repository"):
        public["private_review_repository"] = True
    if arrival.get("keyless_tok_registry"):
        public["keyless_tok_registry"] = True
    public["paths"] = enabled
    return public
