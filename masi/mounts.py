# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""A mount is a pointer. Bytes that do not fit in git are not stored here."""

from __future__ import annotations

from .store import sha256


def mount(filename: str, data: bytes, store: str = "zenodo-via-misty") -> dict:
    return {
        "filename": filename,
        "hash": sha256(data),
        "size": len(data),
        "store": store,
        "external_id": None,
        "provenance": "pointer-only",
    }
