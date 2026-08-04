"""Falsification tests for the ghost-harmless equivalence.

The danger here is overclaim: this is 2x2 linear algebra sitting next to a live
open question about a real theory, and the tests are written to make the
boundary between them mechanical rather than editorial.
"""

from __future__ import annotations

import json
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                    "REVERSE_PHYSICS_GHOST_HARMLESS_V1.json")


def load():
    with open(CERT) as fh:
        return json.load(fh)


class TestTheEquivalence(unittest.TestCase):
    def setUp(self):
        self.cert = load()
        self.cases = {c["case"]: c for c in self.cert["cases"]}

    def test_all_checks_pass(self):
        self.assertTrue(self.cert["checks"]["ok"])
        self.assertEqual(self.cert["checks"]["failures"], [])

    def test_harmless_iff_diagonalizable_and_real_spectrum(self):
        """The robust form, holding in EVERY case including the decoupled one."""
        for c in self.cert["cases"]:
            self.assertEqual(c["harmless"],
                             c["diagonalizable"] and c["real_spectrum"],
                             c["case"])

    def test_the_scan_is_large_and_clean(self):
        s = self.cert["scan"]
        self.assertGreaterEqual(s["points"], 200)
        self.assertEqual(s["mismatch_count"], 0)
        self.assertEqual(s["mismatches"], [])

    def test_both_conditions_have_witnesses(self):
        j, c = self.cases["jordan"], self.cases["complex_pair"]
        # diagonalizability is necessary: real spectrum is not enough
        self.assertTrue(j["real_spectrum"])
        self.assertFalse(j["diagonalizable"])
        self.assertFalse(j["harmless"])
        # real spectrum is necessary: diagonalizability is not enough
        self.assertTrue(c["diagonalizable"])
        self.assertFalse(c["real_spectrum"])
        self.assertFalse(c["harmless"])

    def test_the_harmless_case_exhibits_its_charge(self):
        w = self.cases["real_distinct"]["explicit_positive_charge"]
        self.assertIsNotNone(w, "existence asserted but not exhibited")
        self.assertIn("minor_1", w)
        self.assertIn("det", w)

    def test_every_case_is_pseudo_hermitian(self):
        for c in self.cert["cases"]:
            self.assertTrue(c["is_pseudo_hermitian"], c["case"])

    def test_both_outcomes_occur(self):
        outcomes = {c["harmless"] for c in self.cert["cases"]}
        self.assertEqual(outcomes, {True, False},
                         "a family with one outcome proves nothing")


class TestTheEdgeCaseIsCarried(unittest.TestCase):
    def setUp(self):
        self.cases = {c["case"]: c for c in load()["cases"]}

    def test_the_decoupled_case_is_harmless_with_zero_discriminant(self):
        """Delta = 0 yet harmless -- so the discriminant form of the criterion
        needs b != 0, and this case is what shows it."""
        d = self.cases["decoupled_degenerate"]
        self.assertEqual(d["discriminant"], 0)
        self.assertTrue(d["harmless"])
        self.assertTrue(d["diagonalizable"])
        self.assertTrue(d["real_spectrum"])
        self.assertEqual(d["H"][0][1], 0, "the decoupled case must have b = 0")


class TestItDoesNotOverclaim(unittest.TestCase):
    def setUp(self):
        self.cert = load()

    def test_the_symbolic_identity_is_explicitly_not_claimed(self):
        self.assertTrue(self.cert["identity"]["not_claimed"])
        self.assertIn("not claimed", self.cert["identity"]["why"].lower())

    def test_it_says_the_open_row_stays_open(self):
        joined = " ".join(self.cert["does_not_establish"])
        self.assertIn("C-GHOST-DYNAMICS stays OPEN", joined)

    def test_it_disclaims_the_field_theoretic_ghost(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("finite-dimensional", joined)
        self.assertIn("infinite-dimensional", joined)
        self.assertIn("higher inertia", joined)

    def test_coinciding_is_not_holding(self):
        joined = " ".join(self.cert["does_not_establish"]).lower()
        self.assertIn("coincide is not showing the condition holds", joined)

    def test_it_imports_nothing(self):
        self.assertIn("none", self.cert["imports"].lower())
        self.assertEqual(self.cert["dependency_tags"], ["LOCAL-ALGEBRAIC"])

    def test_the_ledger_row_is_still_open(self):
        """The comparison ledger must not have been quietly closed."""
        with open(os.path.join(
                REPO_ROOT, "reverse_physics", "certificates",
                "REVERSE_PHYSICS_WEYL_VS_EINSTEIN_LEDGER_V1.json")) as fh:
            ledger = json.load(fh)
        row = next(r for r in ledger["rows"] if r["id"] == "C-GHOST-DYNAMICS")
        self.assertEqual(row["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
