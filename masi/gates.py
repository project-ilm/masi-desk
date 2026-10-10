# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gates. G3 blocks a public mint, not an acceptance. G1 compares dates."""

from __future__ import annotations

from .store import Refused


def check(name: str, state: dict, policy: dict, extra: dict | None = None) -> list[str]:
    if name in (policy.get("gates_off") or []):
        return []
    extra = extra or {}
    facts = state.get("facts") or {}
    errors = []
    if name == "G1":
        if facts.get("human_subjects"):
            approved = state["dimensions"].get("irb") in ("approved", "renewed", "amendment", "exempt")
            approved_on = facts.get("approved_on")
            collection_on = extra.get("collection_on") or facts.get("collection_on")
            if not approved:
                errors.append("G1: human-subjects work needs an IRB approval")
            elif approved_on and collection_on and approved_on > collection_on:
                errors.append("G1: approval is dated after collection")
            elif facts.get("expires_on") and extra.get("on") and facts["expires_on"] < extra["on"]:
                errors.append("G1: approval expired; collection is blocked until renewal")
    if name == "G2":
        stamp = facts.get("preregistered_on")
        collection = extra.get("collection_on") or facts.get("collection_on")
        if collection and not stamp:
            errors.append("G2: collection has no preregistration stamp")
        elif stamp and collection and stamp > collection:
            errors.append("G2: preregistration stamp is after collection")
    if name == "G3":
        if extra.get("public_mint") and facts.get("patent_unfiled") and not facts.get("defensive_publication"):
            errors.append("G3: unfiled patent blocks a public mint")
    if name == "G4":
        if extra.get("to") in ("accepted", "included", "published"):
            reviews = [
                item for item in state.get("assessments", [])
                if item.get("kind") == "review" and item.get("round") == state["facts"].get("round", 1)
            ]
            if not reviews:
                errors.append("G4: acceptance needs a recorded review")
    if name == "G5":
        if facts.get("prereg_linked") and facts.get("prereg_state") != "registered":
            errors.append("G5: linked preregistration never reached registered")
    return errors


def require(names: list[str], state: dict, policy: dict, extra: dict | None = None) -> list[str]:
    errors = []
    for name in names:
        errors.extend(check(name, state, policy, extra))
    blocking = [item for item in errors if not item.startswith("G5")]
    if blocking:
        raise Refused("; ".join(blocking))
    return errors
