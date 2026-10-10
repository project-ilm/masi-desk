# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Platform. Each venue is its own directory. The actor must be a linked person."""

from __future__ import annotations

import os
from pathlib import Path

from . import gitprov, records
from .desk import Desk
from .store import Refused


class Platform:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "people").mkdir(exist_ok=True)

    def person(self, person_id: str, name: str, login: str | None = None) -> dict:
        body = {
            "display_name": name,
            "names": [name],
            "logins": {"github": login} if login else {},
            "orcid": None,
            "affiliation": None,
            "can_act": bool(login),
        }
        return records.write(self.root, "person", person_id, body)

    def rename(self, person_id: str, name: str) -> dict:
        current = records.read(self.root, "person", person_id)
        current["names"].append(name)
        current["display_name"] = name
        return records.write(self.root, "person", person_id, current)

    def launch(self, kind: str, title: str, actor: str, owner: str) -> Desk:
        person = records.read(self.root, "person", actor)
        if not person.get("can_act"):
            raise Refused("a person without a forge login cannot act")
        venue = self.root / "venues" / kind / title.replace(" ", "-").lower()
        desk = Desk(venue)
        desk.launch(kind, title, actor)
        records.write(venue, "container", "container", {"kind": kind, "title": title, "owner": owner, "reserved_doi": None, "reserved_state": "pending_external"})
        records.write(venue, "issue", "1", {"volume": 1, "number": 1}) if kind == "journal" else None
        gitprov.commit(venue, f"launch {kind} {title}")
        return desk

    def notify(self, venue: Path, kind: str, recipients: list[str]) -> dict:
        note = records.write(venue, "notification", kind, {"kind": kind, "recipients": recipients, "delivery": "local-adapter", "state": "recorded"})
        gitprov.commit(venue, f"notify {kind}")
        return note

    def credential(self) -> bool:
        return bool(os.environ.get("ZENODO_TOKEN"))
