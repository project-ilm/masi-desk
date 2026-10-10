# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Append-only event store. Current state is a fold. Indexes are projections."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT_FILES = ("policy.json", "container.json")


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Conflict(Exception):
    pass


class Refused(Exception):
    pass


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)

    def init(self, container: dict, policy: dict) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        for name in ("events", "matters", "works", "index", "docket", "mounts", "secrets"):
            (self.path / name).mkdir(exist_ok=True)
        self.write_json("policy.json", policy)
        self.write_json("container.json", container)
        (self.path / "secrets" / ".gitkeep").write_text("", encoding="utf-8")

    def write_json(self, rel: str, obj: dict) -> None:
        target = self.path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(canonical(obj) + "\n", encoding="utf-8")

    def read_json(self, rel: str) -> dict:
        return json.loads((self.path / rel).read_text(encoding="utf-8"))

    def tip(self) -> str | None:
        events = self.events()
        return events[-1]["event_id"] if events else None

    def events(self) -> list[dict]:
        folder = self.path / "events"
        if not folder.exists():
            return []
        out = []
        for path in sorted(folder.glob("*.json")):
            out.append(json.loads(path.read_text(encoding="utf-8")))
        return out

    def append(self, event: dict) -> dict:
        expected = event.get("parent_event")
        tip = self.tip()
        if expected != tip:
            raise Conflict(f"parent {expected} is not tip {tip}")
        body = {k: v for k, v in event.items() if k != "event_id"}
        event_id = sha256(canonical(body).encode())
        event = dict(event)
        event["event_id"] = event_id
        seq = len(self.events()) + 1
        self.write_json(f"events/{seq:06d}-{event_id[:12]}.json", event)
        return event
