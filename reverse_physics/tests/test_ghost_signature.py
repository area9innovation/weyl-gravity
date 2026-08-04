"""Falsification tests for the inertia-(1,2) extension."""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_GHOST_SIGNATURE_V1.json")


def load():
    with open(CERT) as fh:
        return json.load(fh)


class TestTheCriterionSurvives(unittest.TestCase):
    def setUp(self):
        self.cert = load()
        self.by = {c["case"]: c for c in self.cert["cases"]}

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])

    def test_harmless_iff_diagonalizable_and_real(self):
        for c in self.cert["cases"]:
            self.assertEqual(c["harmless"],
                             c["diagonalizable"] and c["real_spectrum"],
                             c["case"])

    def test_both_outcomes_occur(self):
        self.assertEqual({c["harmless"] for c in self.cert["cases"]},
                         {True, False})

    def test_the_two_failure_modes_are_both_present(self):
        """One fails reality, one fails diagonalizability -- the independence
        must still be visible at this inertia."""
        c = self.by["complex_pair"]
        d = self.by["degenerate"]
        self.assertTrue(c["diagonalizable"])
        self.assertFalse(c["real_spectrum"])
        self.assertTrue(d["real_spectrum"])
        self.assertFalse(d["diagonalizable"])

    def test_the_positive_case_exhibits_its_charge(self):
        w = self.by["diagonalizable_real"]["positive_definite_witness"]
        self.assertIsNotNone(w, "existence asserted but not exhibited")
        self.assertEqual(len(w["minors"]), 3)

    def test_every_case_is_pseudo_hermitian(self):
        for c in self.cert["cases"]:
            self.assertTrue(c["is_pseudo_hermitian"], c["case"])


class TestTheFinding(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_two_negative_norm_directions_survive(self):
        sig = self.cert["the_finding"]["eta_signature_in_the_harmless_case"]
        self.assertEqual(sig, [1, -1, -1])
        self.assertEqual(sig.count(-1), 2)

    def test_the_signature_matches_the_declared_inertia(self):
        """(1,2) means one plus and two minus; the eigenbasis must agree."""
        sig = self.cert["the_finding"]["eta_signature_in_the_harmless_case"]
        self.assertEqual((sig.count(1), sig.count(-1)), (1, 2))
        self.assertIn("(1,2)", self.cert["setting"]["krein_metric"])

    def test_the_reading_is_stated(self):
        r = self.cert["the_finding"]["reading"]
        self.assertIn("NOT mean", r)
        self.assertIn("eta-invariant", r)

    def test_it_explains_why_this_was_invisible_at_1_1(self):
        self.assertIn("coincide",
                      self.cert["the_finding"]["why_it_was_invisible_at_1_1"])


class TestItDoesNotOverclaim(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_it_leaves_the_physics_question_open(self):
        joined = " ".join(self.cert["does_not_establish"])
        self.assertIn("Bender--Mannheim", joined)
        self.assertIn("PHYSICS question", joined)

    def test_the_negative_direction_is_not_claimed_exhaustive(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("corroboration rather than proof", joined)

    def test_the_open_row_is_still_open(self):
        self.assertIn("C-GHOST-DYNAMICS stays OPEN",
                      " ".join(self.cert["does_not_establish"]))
        with open(os.path.join(
                REPO_ROOT, "reverse_physics", "certificates",
                "REVERSE_PHYSICS_WEYL_VS_EINSTEIN_LEDGER_V1.json")) as fh:
            ledger = json.load(fh)
        row = next(r for r in ledger["rows"] if r["id"] == "C-GHOST-DYNAMICS")
        self.assertEqual(row["status"], "OPEN")

    def test_it_imports_nothing(self):
        self.assertEqual(self.cert["imports"], "none")
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])


if __name__ == "__main__":
    unittest.main()
