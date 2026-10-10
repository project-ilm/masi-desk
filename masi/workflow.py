# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Transition legality is the matrix of the matter's workflow, not every matrix."""

from __future__ import annotations

import json
from pathlib import Path

from .store import Refused

ROOT = Path(__file__).resolve().parents[1]


def matrix() -> dict:
    return json.loads((ROOT / "transitions.json").read_text(encoding="utf-8"))


def workflow_for(facts: dict) -> str:
    kind = facts.get("workflow") or facts.get("kind")
    if kind in ("chapter",):
        return "chapter"
    if kind in ("appeal",):
        return "appeal"
    if kind in ("irb", "protocol"):
        return "irb"
    if kind in ("conference", "paper") and facts.get("container") == "conference":
        return "conference"
    if facts.get("container") == "conference":
        return "conference"
    if kind == "paper":
        return "journal"
    return kind or "journal"


def legal(workflow: str, previous: str | None, to: str, role: str) -> bool:
    edges = matrix().get(workflow) or []
    role_key = role.split("-")[-1] if role not in ("irb-chair", "handling-editor", "area-chair") else role
    for src, dst, who in edges:
        if dst != to:
            continue
        if src not in ("*", previous):
            continue
        if who in (role, role_key):
            return True
    return False


def require(workflow: str, previous: str | None, to: str, role: str) -> None:
    if not legal(workflow, previous, to, role):
        raise Refused(f"{workflow}: {previous} -> {to} is not allowed for {role}")
