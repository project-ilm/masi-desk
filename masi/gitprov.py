# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Git is the history. A missing commit is a failure, not an invented hash."""

from __future__ import annotations

import subprocess
from pathlib import Path


def ensure(path: Path) -> str | None:
    path.mkdir(parents=True, exist_ok=True)
    if not (path / ".git").exists():
        run = subprocess.run(["git", "init"], cwd=path, capture_output=True, text=True)
        if run.returncode != 0:
            return None
        has = subprocess.run(["git", "config", "user.email"], cwd=path, capture_output=True, text=True).stdout.strip()
        if not has:
            subprocess.run(["git", "config", "user.email", "desk@masi.local"], cwd=path, check=False)
            subprocess.run(["git", "config", "user.name", "MASI desk"], cwd=path, check=False)
    return head(path)


def commit(path: Path, message: str) -> str | None:
    if ensure(path) is None and not (path / ".git").exists():
        return None
    subprocess.run(["git", "add", "-A"], cwd=path, capture_output=True, text=True)
    run = subprocess.run(["git", "commit", "-m", message, "--allow-empty"], cwd=path, capture_output=True, text=True)
    if run.returncode != 0 and "nothing to commit" not in run.stdout + run.stderr:
        return None
    return head(path)


def head(path: Path) -> str | None:
    run = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True)
    if run.returncode != 0:
        return None
    return run.stdout.strip()


def history_lost(path: Path, known: list[str]) -> list[str]:
    run = subprocess.run(["git", "rev-list", "HEAD"], cwd=path, capture_output=True, text=True)
    if run.returncode != 0:
        return known
    present = set(run.stdout.split())
    return [item for item in known if item not in present]
