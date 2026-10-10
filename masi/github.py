# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""GitHub adapter. It calls gh. It does not invent an issue number."""

from __future__ import annotations

import os
import subprocess


def _gh(args: list[str]):
    try:
        return subprocess.run(["gh", *args], capture_output=True, text=True)
    except FileNotFoundError:
        return None


def whoami() -> dict:
    run = _gh(["api", "user", "--jq", ".login"])
    if run is None:
        return {"state": "failed_external", "login": None, "reason": "gh is not installed"}
    if run.returncode != 0:
        return {"state": "failed_external", "login": None, "reason": run.stderr.strip()}
    return {"state": "authenticated", "login": run.stdout.strip(), "reason": None}


def open_issue(title: str, body: str) -> dict:
    repo = os.environ.get("MASI_GITHUB_REPO")
    if not repo:
        return {"state": "pending_external", "number": None, "reason": "MASI_GITHUB_REPO is not set", "url": None}
    run = _gh(["issue", "create", "--repo", repo, "--title", title, "--body", body])
    if run is None:
        return {"state": "failed_external", "number": None, "reason": "gh is not installed", "url": None}
    if run.returncode != 0:
        return {"state": "failed_external", "number": None, "reason": run.stderr.strip(), "url": None}
    url = run.stdout.strip()
    number = url.rstrip("/").split("/")[-1]
    number = int(number) if number.isdigit() else None
    return {"state": "opened", "number": number, "reason": None, "url": url}
