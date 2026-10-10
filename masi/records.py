# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Canonical records. Unknown fields are kept."""

from __future__ import annotations

import json
from pathlib import Path

SCHEMA = "masi-record-2026-10-06"
KINDS = {
    "container", "policy", "person", "matter", "work", "submission", "assessment",
    "review", "decision", "decision-letter", "revision", "event", "session",
    "presentation", "track", "issue", "chapter", "irb", "ip-matter", "notification",
    "docket-entry", "mount",
}


def write(root: Path, kind: str, record_id: str, body: dict) -> dict:
    if kind not in KINDS:
        raise ValueError(kind)
    record = {"schema": SCHEMA, "id": record_id}
    record.update(body)
    record["kind"] = kind
    folder = root / "records" / kind
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{record_id}.json"
    path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    return record


def read(root: Path, kind: str, record_id: str) -> dict:
    return json.loads((root / "records" / kind / f"{record_id}.json").read_text(encoding="utf-8"))
