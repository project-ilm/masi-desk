# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tok and Candor. The stamp is the declared ots client, not misty.ots."""

from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import misty_bridge


def _ayesha(proof: bytes) -> str:
    return "ayesha:" + base64.b64encode(proof).decode()


def _stamp(path: Path) -> bytes:
    ots = shutil.which("ots")
    if ots is None:
        raise RuntimeError("ots client is not installed; pip install opentimestamps-client")
    run = subprocess.run([ots, "stamp", str(path)], capture_output=True, text=True)
    proof = Path(str(path) + ".ots")
    if run.returncode != 0 or not proof.exists():
        raise RuntimeError(run.stderr.strip() or "ots stamp failed")
    data = proof.read_bytes()
    proof.unlink()
    return data


def tok(root: Path, data: bytes, unit: str) -> dict:
    digest = hashlib.sha256(data).hexdigest()
    record = {
        "unit": unit,
        "sha256": digest,
        "meaning": "existence",
        "not": ["authorship", "ownership", "originality", "legal-priority"],
        "ots": None,
        "ayesha": None,
        "state": "pending_external",
        "reason": "ots client not used",
    }
    try:
        scratch = root / ".masi-scratch"
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            path = Path(tmp) / "bytes"
            path.write_bytes(data)
            proof = _stamp(path)
        record["ayesha"] = _ayesha(proof)
        record["ots"] = "stamped"
        record["state"] = "stamped"
        record["reason"] = None
    except Exception as exc:
        record["state"] = "failed_external"
        record["reason"] = str(exc)
    inbox = root / "registry" / "general" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    (inbox / f"{digest}.json").write_text(json.dumps(record) + "\n", encoding="utf-8")
    return record


def guard(root: Path, artifact: Path) -> dict:
    text = artifact.read_text(encoding="utf-8", errors="replace")
    leaked = any(marker in text for marker in ("ZENODO_TOKEN", "ghp_", "BEGIN PRIVATE"))
    # Not misty guard and not spiguard: a three-marker scan. Disclosure checks belong to spiguard.
    return {"tool": "local-marker-scan", "clear": not leaked, "state": "clear" if not leaked else "blocked",
            "note": "a three-marker scan, not a disclosure clearance"}


def candor(root: Path, digest: str, reason: str) -> dict:
    statement = {
        "type": "https://in-toto.io/Statement/v0.1",
        "subject": [{"digest": {"sha256": digest}}],
        "predicate": {"reason": reason},
        "ots": None,
        "ayesha": None,
        "state": "pending_external",
        "reason": "ots client not used",
    }
    folder = root / "attest"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{digest[:16]}.json"
    path.write_text(json.dumps(statement) + "\n", encoding="utf-8")
    try:
        # The proof covers the statement's bytes, so the statement is never rewritten after stamping;
        # the proof is kept beside it.
        proof = _stamp(path)
        statement["ayesha"] = _ayesha(proof)
        statement["ots"] = "stamped"
        statement["state"] = "stamped"
        statement["reason"] = None
        (folder / f"{digest[:16]}.proof.json").write_text(
            json.dumps({"statement": path.name, "ayesha": statement["ayesha"]}) + "\n", encoding="utf-8")
    except Exception as exc:
        statement["state"] = "failed_external"
        statement["reason"] = str(exc)
    return statement


def misty_publish(root: Path, title: str, data: bytes, credential_present: bool) -> dict:
    folder = root / "misty"
    artifact = folder / "artifact.txt"
    folder.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(data)
    misty_bridge.write_metadata(folder, title, "MASI object")
    packaged = misty_bridge.package(folder, artifact)
    rehearsed = misty_bridge.dry_run_publish(folder, artifact)
    if not credential_present:
        return {
            "package": packaged,
            "dry_run": rehearsed,
            "state": "pending_external",
            "reason": "ZENODO_TOKEN is not in the environment",
            "doi": None,
            "minted": False,
        }
    return {"package": packaged, "dry_run": rehearsed, "state": "credential-present-not-called", "doi": None, "minted": False}
