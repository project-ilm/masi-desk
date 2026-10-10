# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import shutil
import os
import tempfile
import unittest
from pathlib import Path

from masi.desk import Desk
from masi.store import Conflict, Refused


def walk(desk, matter, *states):
    last = None
    for state in states:
        last = desk.transition("ed", matter, "editor", state)
    return last


class DeskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.desk = Desk(Path(self.tmp) / "venue")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_launch_three_containers(self):
        for kind in ("journal", "conference", "book"):
            desk = Desk(Path(self.tmp) / kind)
            event = desk.launch(kind, kind, "editor")
            self.assertEqual(event["new_state"], "launched")
            self.assertIsNone(event["parent_event"])

    def test_author_doi_survives_rejection(self):
        self.desk.launch("journal", "Journal", "editor")
        work = self.desk.work("author", "Paper", "10.5281/zenodo.1", b"bytes")
        submitted = self.desk.submit("author", work["matter_id"], "Paper", b"bytes")
        self.desk.assess("rev", submitted["matter_id"], "reviewer", "reject")
        walk(self.desk, submitted["matter_id"], "desk-check", "rejected")
        state = self.desk.recover()[submitted["matter_id"]]
        self.assertEqual(state["facts"]["author_doi"], "10.5281/zenodo.1")
        self.assertEqual(state["dimensions"]["venue"], "rejected")
        self.assertEqual(len(state["assessments"]), 1)

    def test_accept_needs_review_and_later_reject_appends(self):
        self.desk.launch("journal", "Journal", "editor")
        work = self.desk.work("author", "Paper", "10.5281/zenodo.2", b"bytes")
        submitted = self.desk.submit("author", work["matter_id"], "Paper", b"bytes")
        walk(self.desk, submitted["matter_id"], "desk-check", "under-review", "reviews-received")
        with self.assertRaises(Refused):
            self.desk.transition("ed", submitted["matter_id"], "editor", "accepted")
        self.desk.assess("rev", submitted["matter_id"], "reviewer", "accept")
        self.desk.transition("ed", submitted["matter_id"], "editor", "accepted")
        self.desk.assess("rev", submitted["matter_id"], "reviewer", "reject")
        state = self.desk.recover()[submitted["matter_id"]]
        self.assertEqual(len(state["assessments"]), 2)
        self.assertEqual(state["assessments"][0]["recommendation"], "accept")
        self.assertEqual(state["dimensions"]["venue"], "accepted")
        self.assertEqual(state["dimensions"]["review"], "reject")

    def test_parent_conflict(self):
        self.desk.launch("journal", "Journal", "editor")
        tip = self.desk.store.tip()
        self.desk.store.append(
            {
                "event_type": "note",
                "actor": "a",
                "timestamp": "2026-10-06T00:00:00+00:00",
                "matter_id": "x",
                "previous_state": None,
                "new_state": "noted",
                "dimension": "venue",
                "reason": "note",
                "evidence": {},
                "commit": None,
                "parent_event": tip,
                "policy_version": "2026-10-06",
            }
        )
        with self.assertRaises(Conflict):
            self.desk.store.append(
                {
                    "event_type": "note",
                    "actor": "b",
                    "timestamp": "2026-10-06T00:00:01+00:00",
                    "matter_id": "y",
                    "previous_state": None,
                    "new_state": "noted",
                    "dimension": "venue",
                    "reason": "note",
                    "evidence": {},
                    "commit": None,
                    "parent_event": tip,
                    "policy_version": "2026-10-06",
                }
            )

    def test_blind_is_refused_until_it_stops_naming_the_work(self):
        self.desk.launch("conference", "Conf", "chair")
        policy = self.desk.policy
        policy["blind"] = True
        policy["blind_arrival"]["salted_issue"] = True
        self.desk.store.write_json("policy.json", policy)
        work = self.desk.work("author", "Hidden", "10.5281/zenodo.3", b"secret-paper")
        with self.assertRaises(Refused):
            self.desk.submit("author", work["matter_id"], "Hidden", b"secret-paper", salt="not-public-pepper")

    def test_a_salt_needs_a_named_store_and_the_index_regenerates(self):
        self.desk.launch("conference", "Conf", "chair")
        work = self.desk.work("author", "Open", "10.5281/zenodo.3", b"open-paper")
        old = os.environ.pop("MASI_SECRET_STORE", None)
        try:
            with self.assertRaises(Refused):
                self.desk.submit("author", work["matter_id"], "Open", b"open-paper", salt="not-public-pepper")
            os.environ["MASI_SECRET_STORE"] = os.path.join(self.tmp, "unblinder")
            self.desk.submit("author", work["matter_id"], "Open", b"open-paper", salt="not-public-pepper")
            self.assertTrue(os.listdir(os.environ["MASI_SECRET_STORE"]))
        finally:
            os.environ.pop("MASI_SECRET_STORE", None)
            if old is not None:
                os.environ["MASI_SECRET_STORE"] = old
        index = self.desk.rebuild_index()
        self.assertNotIn("not-public-pepper", json.dumps(index))
        self.assertEqual(index, self.desk.rebuild_index())

    def test_a_short_key_is_refused_not_padded(self):
        with self.assertRaises(ValueError):
            self.desk.encrypt_review(b"comments", b"short-key")

    def test_irb_gate_and_session_and_docket_and_ip(self):
        self.desk.launch("journal", "Journal", "editor")
        work = self.desk.work("author", "Study", "10.5281/zenodo.4", b"study")
        submitted = self.desk.submit("author", work["matter_id"], "Study", b"study")
        self.desk.store.append(
            {
                "event_type": "fact",
                "actor": "author",
                "timestamp": "2026-10-06T00:00:00+00:00",
                "matter_id": submitted["matter_id"],
                "previous_state": None,
                "new_state": submitted["new_state"],
                "dimension": "venue",
                "reason": "fact",
                "evidence": {"human_subjects": True, "kind": "paper"},
                "commit": None,
                "parent_event": self.desk.store.tip(),
                "policy_version": "2026-10-06",
            }
        )
        self.desk.assess("rev", submitted["matter_id"], "reviewer", "accept")
        walk(self.desk, submitted["matter_id"], "desk-check", "under-review", "reviews-received", "accepted")
        walk(self.desk, submitted["matter_id"], "copyedit", "proof")
        with self.assertRaises(Refused):
            self.desk.transition("ed", submitted["matter_id"], "editor", "published")
        self.desk.irb("chair", submitted["matter_id"], "approved", {"approved_on": "2020-01-01", "approval_id": "IRB-1", "expires_on": "2027-01-01"})
        self.desk.transition("ed", submitted["matter_id"], "editor", "published")
        session = self.desk.session("chair", "main", submitted["matter_id"])
        self.assertEqual(session["new_state"], "scheduled")
        row = self.desk.docket("author", work["matter_id"], "Conf", submitted["matter_id"])
        self.assertEqual(row["doi"], "10.5281/zenodo.4")
        ip = self.desk.ip("author", "patent-1", "patent", "drafting")
        self.assertEqual(ip["dimension"], "ip")
        packed = self.desk.encrypt_review(b"comments", b"0123456789abcdef0123456789abcdef")
        self.assertEqual(packed["scheme"], "AES-GCM")
        self.assertNotIn("comments", packed["ciphertext"])
        pushed = self.desk.rehearse_outlet({"hash": "abc", "title": "Study"})
        self.assertTrue(pushed["rehearsal"])
        self.assertFalse(pushed["pushed"])
        self.desk.appeal("author", submitted["matter_id"], "requested")
        recovered = self.desk.recover()
        self.assertIn(submitted["matter_id"], recovered)

    def test_g3_blocks_mint_not_acceptance(self):
        self.desk.launch("journal", "Journal", "editor")
        work = self.desk.work("author", "Claim", "10.5281/zenodo.5", b"claim")
        submitted = self.desk.submit("author", work["matter_id"], "Claim", b"claim")
        self.desk.store.append(
            {
                "event_type": "fact",
                "actor": "author",
                "timestamp": "2026-10-06T00:00:00+00:00",
                "matter_id": submitted["matter_id"],
                "previous_state": None,
                "new_state": "submitted",
                "dimension": "venue",
                "reason": "fact",
                "evidence": {"patent_unfiled": True, "kind": "paper"},
                "commit": None,
                "parent_event": self.desk.store.tip(),
                "policy_version": "2026-10-06",
            }
        )
        self.desk.assess("rev", submitted["matter_id"], "reviewer", "accept")
        accepted = walk(self.desk, submitted["matter_id"], "desk-check", "under-review", "reviews-received", "accepted")
        self.assertEqual(accepted["new_state"], "accepted")
        with self.assertRaises(Refused):
            walk(self.desk, submitted["matter_id"], "copyedit", "proof", "published")

    def test_encryption_hides_plaintext(self):
        self.desk.launch("journal", "Journal", "editor")
        key = b"0123456789abcdef0123456789abcdef"
        packed = self.desk.encrypt_review(b"confidential comments", key)
        self.assertNotIn("confidential", packed["ciphertext"])
        self.assertEqual(self.desk.decrypt_review(key), b"confidential comments")

    def test_g1_date_and_book_chapters(self):
        book = Desk(Path(self.tmp) / "book")
        book.launch("book", "Book", "editor")
        recovered = book.recover()
        self.assertIn("chapter-4", recovered)
        self.desk.launch("journal", "Journal", "editor")
        work = self.desk.work("author", "Study", "10.5281/zenodo.9", b"study")
        submitted = self.desk.submit("author", work["matter_id"], "Study", b"study")
        self.desk.store.append(
            {
                "event_type": "fact",
                "actor": "author",
                "timestamp": "2026-10-06T00:00:00+00:00",
                "matter_id": submitted["matter_id"],
                "previous_state": "submitted",
                "new_state": "submitted",
                "dimension": "venue",
                "reason": "fact",
                "evidence": {"human_subjects": True, "collection_on": "2026-02-01", "kind": "paper"},
                "commit": None,
                "parent_event": self.desk.store.tip(),
                "policy_version": "2026-10-06",
            }
        )
        self.desk.assess("rev", submitted["matter_id"], "reviewer", "accept")
        walk(self.desk, submitted["matter_id"], "desk-check", "under-review", "reviews-received", "accepted")
        self.desk.irb("chair", submitted["matter_id"], "approved", {"approved_on": "2026-03-01", "approval_id": "IRB-9"})
        with self.assertRaises(Refused):
            walk(self.desk, submitted["matter_id"], "copyedit", "proof", "published")

    def test_matrix_is_bound_to_workflow_and_misty_is_called(self):
        self.desk.launch("journal", "Journal", "editor")
        work = self.desk.work("author", "Paper", "10.5281/zenodo.8", b"bytes")
        submitted = self.desk.submit("author", work["matter_id"], "Paper", b"bytes")
        with self.assertRaises(Refused):
            self.desk.transition("ed", submitted["matter_id"], "editor", "abstract-accepted")
        result = self.desk.mint_with_misty("Paper", b"bytes")
        self.assertEqual(result["packaged"]["tool"], "misty-doi")
        self.assertFalse(result["minted"])
        self.assertIsNone(result["packaged"]["doi"])
        if result["packaged"].get("state") == "pending_external":
            self.assertIn("misty", result["packaged"]["reason"])
        else:
            self.assertEqual(result["packaged"]["exit"], 0)

    def test_cli_launch(self):
        from masi.__main__ import main

        code = main(["--venue", str(Path(self.tmp) / "cli"), "launch", "book", "Four chapters"])
        self.assertEqual(code, 0)
        self.assertTrue((Path(self.tmp) / "cli" / "events").exists())


if __name__ == "__main__":
    unittest.main()
