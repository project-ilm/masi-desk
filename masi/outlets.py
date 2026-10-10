# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Outlet adapter. Local rehearsal records the push. It does not mint."""

from __future__ import annotations


class LocalOutlet:
    name = "local"

    def __init__(self):
        self.calls = []

    def prepare(self, package: dict) -> dict:
        self.calls.append(("prepare", package))
        return package

    def validate(self, package: dict) -> None:
        if not package.get("hash"):
            raise ValueError("outlet package needs a hash")
        self.calls.append(("validate", package["hash"]))

    def push(self, package: dict) -> dict:
        self.calls.append(("push", package.get("hash")))
        return {"external_id": "local:" + package["hash"][:12], "pushed": False, "rehearsal": True}

    def record_failure(self, reason: str) -> dict:
        self.calls.append(("failure", reason))
        return {"failure": reason}
