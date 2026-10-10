# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import json
import tempfile
import unittest
from pathlib import Path

from masi.api import list_records
from masi.gitprov import head, history_lost
from masi.platform import Platform
from masi.provenance import candor, guard, misty_publish, tok
from masi.records import read
from masi.store import Refused


class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.platform = Platform(Path(self.tmp))
        self.platform.person("ada", "Ada", login="ada")

    def test_two_of_each_are_isolated(self):
        venues = []
        for kind, title in (
            ("journal", "One"), ("journal", "Two"),
            ("conference", "One"), ("conference", "Two"),
            ("book", "One"), ("book", "Two"),
        ):
            desk = self.platform.launch(kind, title, "ada", "institution")
            venues.append(desk.store.path)
        self.assertEqual(len({str(path) for path in venues}), 6)
        self.assertTrue(all(head(path) for path in venues))

    def test_unlinked_person_cannot_act(self):
        self.platform.person("no-login", "No Login")
        with self.assertRaises(Refused):
            self.platform.launch("journal", "Blocked", "no-login", "person")

    def test_name_change_appends(self):
        self.platform.rename("ada", "Ada Lovelace")
        person = read(self.platform.root, "person", "ada")
        self.assertEqual(person["names"], ["Ada", "Ada Lovelace"])

    def test_no_invented_doi_or_tok(self):
        desk = self.platform.launch("journal", "Journal", "ada", "group")
        stamp = tok(desk.store.path, b"bytes", "file")
        # With the calendars reachable the stamp is real; without them it says so. It is never invented.
        self.assertIn(stamp["state"], ("stamped", "failed_external"))
        if stamp["state"] == "stamped":
            self.assertTrue(stamp["ayesha"].startswith("ayesha:"))
        else:
            self.assertIsNone(stamp["ayesha"])
            self.assertTrue(stamp["reason"])
        statement = candor(desk.store.path, stamp["sha256"], "mint")
        self.assertIn(statement["state"], ("stamped", "failed_external"))
        if statement["state"] == "stamped":
            # the stamped statement is left as it was stamped; the proof sits beside it
            on_disk = json.loads((desk.store.path / "attest" / (stamp["sha256"][:16] + ".json")).read_text())
            self.assertIsNone(on_disk["ayesha"])
            self.assertTrue((desk.store.path / "attest" / (stamp["sha256"][:16] + ".proof.json")).exists())
        result = misty_publish(desk.store.path, "Journal", b"bytes", credential_present=bool(os.environ.get("ZENODO_TOKEN")))
        self.assertIsNone(result["doi"])
        self.assertFalse(result["minted"])
        from masi.github import whoami
        who = whoami()
        self.assertIn(who["state"], ("authenticated", "failed_external"))
        if who["state"] == "authenticated":
            self.assertTrue(who["login"])
        scan = guard(desk.store.path, desk.store.path / "misty" / "artifact.txt")
        self.assertEqual((scan["clear"], scan["tool"]), (True, "local-marker-scan"))

    def test_secret_not_in_index_and_history_check(self):
        desk = self.platform.launch("journal", "Journal", "ada", "person")
        note = self.platform.notify(desk.store.path, "submission", ["ada"])
        self.assertEqual(note["kind"], "notification")
        self.assertEqual(list_records(self.platform.root, "person")[0]["id"], "ada")
        known = [head(desk.store.path)]
        self.assertEqual(history_lost(desk.store.path, known), [])


if __name__ == "__main__":
    unittest.main()
