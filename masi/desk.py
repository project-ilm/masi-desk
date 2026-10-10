# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Desk operations. Launch, submit, transition, index. No mint is performed here."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from . import blind, gates, indexes, mounts, permissions
from .encryption import open_seal, seal
from .fold import fold, fold_all
from .outlets import LocalOutlet
from . import gitprov
from . import workflow
from . import misty_bridge
from .store import Refused, Store, sha256
from .store import Refused, Store, sha256

DEFAULT_POLICY = {
    "policy_version": "2026-10-06",
    "priority": "on-accept",
    "reviews": "closed",
    "review_as_version": False,
    "blind": False,
    "blind_arrival": {
        "salted_issue": False,
        "ciphertext": False,
        "private_review_repository": False,
        "keyless_tok_registry": False,
    },
    "conference": {"registration": False, "invitation_letters": False, "visa_letters": False},
    "gates_off": [],
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Desk:
    def __init__(self, path: Path):
        self.store = Store(path)
        self.outlet = LocalOutlet()

    @property
    def policy(self) -> dict:
        return self.store.read_json("policy.json")

    def launch(self, kind: str, title: str, actor: str) -> dict:
        policy = dict(DEFAULT_POLICY)
        container = {
            "kind": kind,
            "title": title,
            "license": "GPL-3.0-or-later",
            "policy_version": policy["policy_version"],
            "reserved_doi": None,
        }
        self.store.init(container, policy)
        evidence = {"kind": kind, "title": title}
        if kind == "journal":
            evidence["issue"] = {"volume": 1, "number": 1}
        if kind == "book":
            evidence["chapters"] = []
            event = self._event("launch", actor, "container", None, "launched", "venue", evidence)
            for number in range(1, 5):
                chapter_id = f"chapter-{number}"
                self._event(
                    "chapter",
                    actor,
                    chapter_id,
                    None,
                    "proposed",
                    "venue",
                    {"kind": "chapter", "order": number, "title": chapter_id, "role": "front" if number == 1 else "chapter"},
                )
                evidence["chapters"].append(chapter_id)
            return event
        if kind == "conference":
            evidence["tracks"] = []
            event = self._event("launch", actor, "container", None, "launched", "venue", evidence)
            self._event(
                "track",
                actor,
                "track-main",
                None,
                "open",
                "program",
                {"kind": "track", "track": "main", "chair": actor, "quota": None},
            )
            evidence["tracks"].append("main")
            return event
        return self._event("launch", actor, "container", None, "launched", "venue", evidence)

    def work(self, actor: str, title: str, author_doi: str, data: bytes) -> dict:
        work_id = sha256(data)
        self.store.write_json(
            f"works/{work_id}.json",
            {"work_id": work_id, "title": title, "author_doi": author_doi, "hash": work_id},
        )
        return self._event(
            "work",
            actor,
            work_id,
            None,
            "minted-by-author",
            "publication",
            {"kind": "work", "title": title, "author_doi": author_doi, "hash": work_id},
        )

    def submit(self, actor: str, work_id: str, title: str, data: bytes, salt: str | None = None) -> dict:
        if self.policy.get("blind"):
            raise Refused("blind arrival is refused in this release: the public venue repository still names the "
                          "title and the author DOI in works/, matters/, events/ and the index (docs/CHECK.md, B1)")
        work = self.store.read_json(f"works/{work_id}.json")
        pointer = mounts.mount(title, data) if len(data) > 1024 else {"hash": sha256(data), "size": len(data)}
        arrival = blind.apply(self.policy, work["author_doi"], salt)
        container = self.store.read_json("container.json")
        evidence = {
            "kind": "paper",
            "workflow": "conference" if container.get("kind") == "conference" else "journal",
            "container": container.get("kind"),
            "title": title,
            "work_id": work_id,
            "author_doi": work["author_doi"],
            "hash": pointer["hash"],
            "mount": pointer if pointer.get("store") else None,
            "issue": 1,
            "round": 1,
        }
        evidence.update({k: v for k, v in arrival.items() if k != "mode"})
        if salt:
            if not os.environ.get("MASI_SECRET_STORE"):
                raise Refused("a salt is held by the unblinder: name its store in MASI_SECRET_STORE; it never defaults")
            secret_root = Path(os.environ["MASI_SECRET_STORE"])
            secret_root.mkdir(parents=True, exist_ok=True)
            (secret_root / f"{pointer['hash']}.salt").write_text(salt, encoding="utf-8")
        return self._event("submit", actor, "matter-" + pointer["hash"][:12], "prepared", "submitted", "venue", evidence)

    def assess(self, actor: str, matter_id: str, role: str, recommendation: str) -> dict:
        if not permissions.allow(role, "review") and not permissions.allow(role, "decide"):
            raise Refused(f"{role} cannot assess")
        state = fold(self.store.events(), matter_id)
        return self._event(
            "assessment",
            actor,
            matter_id,
            state["dimensions"].get("review"),
            recommendation,
            "review",
            {"recommendation": recommendation, "role": role, "kind": "review", "round": state["facts"].get("round", 1), "hash": state["facts"].get("hash")},
        )

    def transition(self, actor: str, matter_id: str, role: str, to: str, dimension: str = "venue") -> dict:
        action = {"accepted": "accept", "rejected": "reject", "published": "publish", "withdrawn": "withdraw"}.get(to, "decide")
        matrix = permissions.load(Path(__file__).resolve().parents[1] / "permissions.json")
        if not permissions.allow(role, action, matrix) and not permissions.allow(role, "decide", matrix):
            raise Refused(f"{role} cannot {to}")
        state = fold(self.store.events(), matter_id)
        grant = self.store.path / "grants" / f"{state['facts'].get('track', 'main')}-{actor}.json"
        if grant.exists():
            scoped = json.loads(grant.read_text(encoding="utf-8"))
            if scoped.get("scope") != "track":
                raise Refused("a track grant is not a repository grant")
        state = fold(self.store.events(), matter_id)
        workflow.require(workflow.workflow_for(state["facts"]), state["dimensions"].get(dimension), to, role)
        if to in ("accepted", "included", "published", "proceedings-published"):
            gates.require(["G4"], state, self.policy, {"to": to})
        if to in ("published", "proceedings-published"):
            gates.require(["G1", "G3"], state, self.policy, {"to": to, "public_mint": True})
        return self._event("transition", actor, matter_id, state["dimensions"].get(dimension), to, dimension, {})

    def irb(self, actor: str, matter_id: str, to: str, evidence: dict | None = None) -> dict:
        if not permissions.allow("irb-chair", "approve"):
            raise Refused("irb")
        evidence = dict(evidence or {})
        evidence.setdefault("kind", "irb")
        evidence["irb"] = to
        if to in ("approved", "renewed", "amendment") and not evidence.get("approved_on"):
            raise Refused("IRB approval needs approved_on")
        if to == "approved" and not evidence.get("approval_id"):
            raise Refused("IRB approval needs an approval identifier")
        state = fold(self.store.events(), matter_id)
        return self._event("irb", actor, matter_id, state["dimensions"].get("irb"), to, "irb", evidence)

    def session(self, actor: str, track: str, paper_id: str) -> dict:
        paper = fold(self.store.events(), paper_id)
        if paper["dimensions"].get("venue") not in ("accepted", "published", "camera-ready", "presented"):
            raise Refused("a presentation needs an accept standing")
        session_id = "session-" + track
        record = {"kind": "session", "track": track, "chair": actor, "start": None, "end": None, "room": "label", "presentations": [paper_id]}
        self.store.write_json(f"sessions/{session_id}.json", record)
        self.store.write_json(f"presentations/{paper_id}.json", {"paper": paper_id, "session": session_id, "kind": "talk"})
        return self._event("session", actor, session_id, None, "scheduled", "program", record)

    def appeal(self, actor: str, matter_id: str, to: str, role: str = "author") -> dict:
        appeal_id = "appeal-" + matter_id
        state = fold(self.store.events(), appeal_id)
        previous = state["dimensions"].get("review")
        if to == "requested" and previous is None:
            return self._event("appeal", actor, appeal_id, None, "requested", "review", {"kind": "appeal", "workflow": "appeal", "target": matter_id})
        workflow.require("appeal", previous, to, role)
        return self._event("appeal", actor, appeal_id, previous, to, "review", {"kind": "appeal", "workflow": "appeal", "target": matter_id})

    def mint_with_misty(self, title: str, data: bytes) -> dict:
        folder = self.store.path / "misty"
        artifact = folder / "artifact.txt"
        folder.mkdir(parents=True, exist_ok=True)
        artifact.write_bytes(data)
        misty_bridge.write_metadata(folder, title, "MASI venue artifact")
        packaged = misty_bridge.package(folder, artifact)
        rehearsed = misty_bridge.dry_run_publish(folder, artifact)
        return {"packaged": packaged, "rehearsed": rehearsed, "minted": False}

    def docket(self, actor: str, work_id: str, venue: str, matter_id: str) -> dict:
        state = fold(self.store.events(), matter_id)
        row = {
            "work_id": work_id,
            "venue": venue,
            "matter_id": matter_id,
            "venue_state": state["dimensions"].get("venue"),
            "doi": state["facts"].get("author_doi"),
        }
        self.store.write_json(f"docket/{work_id}-{matter_id}.json", row)
        return row

    def ip(self, actor: str, matter_id: str, right: str, state_name: str) -> dict:
        return self._event("ip", actor, matter_id, None, state_name, "ip", {"kind": right, "right": right})

    def encrypt_review(self, body: bytes, reviewer_key: bytes) -> dict:
        packed = seal(body, reviewer_key)
        self.store.write_json("matters/review-envelope.json", packed)
        if body.decode() in packed["ciphertext"]:
            raise Refused("plaintext leaked into ciphertext")
        return packed

    def decrypt_review(self, reviewer_key: bytes) -> bytes:
        return open_seal(self.store.read_json("matters/review-envelope.json"), reviewer_key)

    def rebuild_index(self) -> dict:
        events = self.store.events()
        paper_index = indexes.papers(events, self.policy)
        session_index = indexes.sessions(events)
        self.store.write_json("index/papers.json", paper_index)
        self.store.write_json("index/sessions.json", session_index)
        return paper_index

    def recover(self) -> dict:
        return fold_all(self.store.events())

    def rehearse_outlet(self, package: dict) -> dict:
        self.outlet.prepare(package)
        self.outlet.validate(package)
        return self.outlet.push(package)

    def _event(self, event_type, actor, matter_id, previous, new, dimension, evidence) -> dict:
        event = self.store.append(
            {
                "event_type": event_type,
                "actor": actor,
                "timestamp": now(),
                "matter_id": matter_id,
                "previous_state": previous,
                "new_state": new,
                "dimension": dimension,
                "reason": event_type,
                "evidence": evidence,
                "commit": None,
                "parent_event": self.store.tip(),
                "policy_version": self.policy["policy_version"],
            }
        )
        self.store.write_json(f"matters/{matter_id}.json", fold(self.store.events(), matter_id))
        sha = gitprov.commit(self.store.path, f"{event_type} {matter_id}")
        # commit is the repository state associated with the transition, not the commit that contains this field. Embedding the SHA of the commit that contains the SHA cannot be done in one write.
        event["commit"] = sha
        self.store.write_json(f"events/{len(self.store.events()):06d}-{event['event_id'][:12]}.json", event)
        return event
