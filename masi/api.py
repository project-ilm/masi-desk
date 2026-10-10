# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""API boundary. Reads records. Does not mint."""

from __future__ import annotations

import json
from pathlib import Path


def list_records(root: Path, kind: str) -> list[dict]:
    folder = Path(root) / "records" / kind
    if not folder.exists():
        return []
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(folder.glob("*.json"))]
