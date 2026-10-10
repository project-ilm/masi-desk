# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Calls misty-doi. Package and dry-run are real. A live mint needs a token."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

def _quiet(fn, argv):
    """Run misty's CLI in-process without letting it write to the caller's stdout; keep what it said."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = fn(argv)
    return code, out.getvalue()


def _misty():
    try:
        from misty.cli import main as misty_main
    except ImportError as exc:
        return None, str(exc)
    return misty_main, None


def write_metadata(directory: Path, title: str, description: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    meta = {
        "title": title,
        "version": "1.0.0",
        "upload_type": "publication",
        "publication_type": "article",
        "description": description,
        "license": "gpl-3.0",
        "access_right": "open",
        "creators": [{"name": "Choudhary, Abhishek", "affiliation": "AyeAI", "orcid": ""}],
        "keywords": ["masi"],
        "related_identifiers": [],
        "repository": "",
    }
    path = directory / "misty.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return path


def package(directory: Path, artifact: Path) -> dict:
    misty_main, error = _misty()
    if misty_main is None:
        return {"tool": "misty-doi", "command": "package", "exit": None, "doi": None, "minted": False, "state": "pending_external", "reason": error}
    meta = directory / "misty.json"
    code, said = _quiet(misty_main, ["package", "-m", str(meta), "-f", str(artifact), "-o", str(directory / "doi-package")])
    return {"tool": "misty-doi", "command": "package", "exit": code, "doi": None, "minted": False, "output": said}


def dry_run_publish(directory: Path, artifact: Path) -> dict:
    misty_main, error = _misty()
    if misty_main is None:
        return {"tool": "misty-doi", "command": "publish --dry-run", "exit": None, "doi": None, "minted": False, "state": "pending_external", "reason": error}
    meta = directory / "misty.json"
    code, said = _quiet(misty_main, [
        "publish", "-m", str(meta), "-f", str(artifact), "--dry-run", "--no-package",
    ])
    return {"tool": "misty-doi", "command": "publish --dry-run", "exit": code, "doi": None, "minted": False, "output": said}
