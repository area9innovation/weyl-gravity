"""Falsification tests for the Bateman-Turok vs Mannheim ledger.

A comparison ledger fails in two characteristic ways and both are tested.

It can COLLAPSE: every row pointing the same direction, which means the axis is
decorative and the ledger is really a verdict wearing a table's clothes.

Or it can go VACUOUS: rows with no source, so the ledger asserts relations it
does not hold evidence for.  The whole point of this file is that the ledger
adjudicates nothing -- if a row ever stops citing something proved elsewhere,
it has quietly become an opinion.
"""

from __future__ import annotations

import importlib.util
import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_BATEMAN_VS_MANNHEIM_LEDGER_V1.json")
MODULE = os.path.join(REPO_ROOT, "reverse_physics",
                      "bateman_vs_mannheim_ledger.py")


def module():
    spec = importlib.util.spec_from_file_location("bvm", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestGate(unittest.TestCase):
    def setUp(self):
        with open(CERT) as fh:
            self.cert = json.load(fh)

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"],
                        self.cert["checks"]["failures"])

    def test_tag_and_lifecycle(self):
        self.assertEqual(self.cert["dependency_tag"], "LOCAL-ALGEBRAIC")
        self.assertEqual(self.cert["lifecycle_state"], "CLASSIFIED")

    def test_it_adjudicates_nothing(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("adjudication", joined)
        self.assertIn("any new physics", joined)


class TestTheAxisIsForced(unittest.TestCase):
    def setUp(self):
        self.m = module()

    def test_truth_value_actually_flips(self):
        """Without a flip the level axis would be unnecessary."""
        by_id = {r["level"]: r for r in self.m.LEVELS}
        self.assertIs(by_id["L2"]["agree"], True)
        self.assertIs(by_id["L4"]["agree"], False)

    def test_ledger_does_not_collapse_to_one_direction(self):
        directions = {r["direction"] for r in self.m.LEVELS}
        self.assertGreaterEqual(len(directions), 3)
        self.assertIn("SHARED", directions)
        self.assertIn("BOTH-STOP", directions)

    def test_every_level_cites_a_source(self):
        for r in self.m.LEVELS:
            self.assertTrue(r.get("source"), r["level"])


class TestComplementarity(unittest.TestCase):
    def setUp(self):
        self.m = module()

    def test_each_programme_survives_some_witness(self):
        """If one survived both, it would dominate rather than complement."""
        survivors = {w["survivor"] for w in self.m.WITNESSES}
        self.assertEqual(survivors, {"mannheim", "bateman_turok"})

    def test_every_witness_cites_a_source(self):
        for w in self.m.WITNESSES:
            self.assertTrue(w.get("source"), w["drop"])

    def test_the_two_fillings_are_genuinely_opposed(self):
        slot = self.m.SLOT
        self.assertNotEqual(slot["mannheim"]["filling"],
                            slot["bateman_turok"]["filling"])
        self.assertNotEqual(slot["mannheim"]["keeps_field_real"],
                            slot["bateman_turok"]["keeps_field_real"])


class TestCrossFertilizationIsGraded(unittest.TestCase):
    """Speculative transfers must stay labelled as such."""

    def setUp(self):
        self.m = module()

    def test_speculative_entries_are_flagged(self):
        spec = [c for c in self.m.CROSS if "speculative" in c["strength"]]
        self.assertTrue(spec)
        for c in spec:
            self.assertIn("not established", c["content"].lower())

    def test_concrete_entries_exist_and_are_distinct(self):
        conc = [c for c in self.m.CROSS if c["strength"] == "concrete"]
        self.assertGreaterEqual(len(conc), 1)
        self.assertEqual(len({c["direction"] for c in conc}), len(conc))

    def test_repository_transfer_is_an_exact_obstruction(self):
        row = [c for c in self.m.CROSS
               if c["direction"] == "this repository -> BT"][0]
        self.assertEqual(row["strength"], "exact obstruction")
        self.assertIn("nonstationary", row["content"])
        self.assertIn("non-mass", row["content"])

    def test_the_bt_to_mannheim_transfer_names_the_mechanism(self):
        bt = [c for c in self.m.CROSS
              if c["direction"] == "BT -> Mannheim"][0]
        self.assertIn("second-order", bt["content"])
        self.assertIn("variable", bt["content"])


if __name__ == "__main__":
    unittest.main()
