# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Permissions load from permissions.json. Track grants are files, not repository roles."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT = {
    "author": ["submit", "revise", "withdraw", "retract-own"],
    "co-author": ["submit", "revise", "withdraw"],
    "corresponding-author": ["submit", "revise", "withdraw", "retract-own"],
    "reviewer": ["review", "decline"],
    "handling-editor": ["assign", "decide", "accept", "reject", "publish", "policy"],
    "area-chair": ["assign", "decide", "accept", "reject"],
    "editor": ["assign", "decide", "accept", "reject", "publish", "retract-venue", "policy"],
    "chair": ["assign", "decide", "accept", "reject", "publish", "retract-venue", "policy", "grant-track"],
    "board": ["read-public", "policy"],
    "irb-member": ["review"],
    "irb-chair": ["approve", "refuse", "amend", "renew", "decide"],
    "reader": ["read-public"],
}


def load(path: Path | None = None) -> dict:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return DEFAULT


def allow(role: str, action: str, matrix: dict | None = None) -> bool:
    table = matrix or DEFAULT
    return action in table.get(role, [])


def grant_track(store_path: Path, person: str, track: str, role: str) -> dict:
    grant = {"person": person, "track": track, "role": role, "scope": "track"}
    target = store_path / "grants" / f"{track}-{person}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(grant), encoding="utf-8")
    return grant

