# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fold events into a multi-dimensional matter state. Not one scalar."""

from __future__ import annotations

DIMENSIONS = ("venue", "review", "publication", "program", "irb", "ip")


def empty_state(matter_id: str) -> dict:
    return {
        "matter_id": matter_id,
        "dimensions": {name: None for name in DIMENSIONS},
        "facts": {},
        "assessments": [],
        "policy_versions": [],
        "links": {},
    }


def fold(events: list[dict], matter_id: str) -> dict:
    state = empty_state(matter_id)
    for event in events:
        if event.get("matter_id") != matter_id:
            continue
        dim = event.get("dimension") or "venue"
        if dim not in state["dimensions"]:
            state["dimensions"][dim] = None
        state["dimensions"][dim] = event.get("new_state")
        if event.get("policy_version"):
            state["policy_versions"].append(
                {"event_id": event["event_id"], "policy_version": event["policy_version"]}
            )
        if event.get("event_type") == "assessment":
            state["assessments"].append(
                {
                    "event_id": event["event_id"],
                    "recommendation": event.get("evidence", {}).get("recommendation"),
                    "kind": event.get("evidence", {}).get("kind", "review"),
                    "round": event.get("evidence", {}).get("round", 1),
                    "at": event.get("timestamp"),
                    "actor": event.get("actor"),
                }
            )
        facts = event.get("evidence") or {}
        for key, value in facts.items():
            if key == "secret":
                continue
            state["facts"][key] = value
        if event.get("event_type") == "link":
            state["links"][facts.get("rel", "related")] = facts.get("target")
    state["latest_assessment"] = state["assessments"][-1] if state["assessments"] else None
    return state


def fold_all(events: list[dict]) -> dict[str, dict]:
    ids = []
    for event in events:
        mid = event.get("matter_id")
        if mid and mid not in ids:
            ids.append(mid)
    return {mid: fold(events, mid) for mid in ids}
