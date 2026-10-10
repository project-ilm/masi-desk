# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Indexes are regenerated from events. They are not a source of truth."""

from __future__ import annotations

from .fold import fold_all


def papers(events: list[dict], policy: dict) -> dict:
    folded = fold_all(events)
    rows = []
    for matter_id, state in folded.items():
        if state["facts"].get("kind") not in ("paper", "chapter", "article", None) and state["facts"].get("kind") not in (
            "paper",
            "article",
            "chapter",
        ):
            continue
        if not state["facts"].get("kind"):
            continue
        title = state["facts"].get("title")
        blind = policy.get("blind") and any(policy.get("blind_arrival", {}).values())
        rows.append(
            {
                "matter_id": matter_id,
                "issue": state["facts"].get("issue"),
                "title": None if blind and state["facts"].get("salted_hash") else title,
                "salted_hash": state["facts"].get("salted_hash"),
                "track": state["facts"].get("track"),
                "venue_state": state["dimensions"].get("venue"),
                "review_state": state["dimensions"].get("review"),
                "publication_state": state["dimensions"].get("publication"),
                "program_state": state["dimensions"].get("program"),
                "doi": state["facts"].get("author_doi") or state["facts"].get("doi"),
                "work_id": state["facts"].get("work_id"),
            }
        )
    return {"papers": rows}


def sessions(events: list[dict]) -> dict:
    folded = fold_all(events)
    rows = []
    for matter_id, state in folded.items():
        if state["facts"].get("kind") != "session":
            continue
        rows.append(
            {
                "matter_id": matter_id,
                "track": state["facts"].get("track"),
                "chair": state["facts"].get("chair"),
                "start": state["facts"].get("start"),
                "end": state["facts"].get("end"),
                "room": state["facts"].get("room"),
                "presentations": state["facts"].get("presentations") or [],
            }
        )
    return {"sessions": rows}
