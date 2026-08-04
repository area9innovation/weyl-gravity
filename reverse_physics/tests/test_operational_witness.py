"""Falsification tests for the operational bridge."""

from __future__ import annotations

import json
import os
import unittest

# The module needs sympy, which the fast suite's interpreter does not have, so
# these tests read the EMITTED CERTIFICATE rather than importing -- the same
# convention the other sympy-backed rails in this directory use.  The exhaustive
# rail is `python3 -m reverse_physics.operational_witness --check` on the mise
# interpreter.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT_PATH = os.path.join(REPO_ROOT, "reverse_physics", "certificates",
                         "REVERSE_PHYSICS_OPERATIONAL_WITNESS_V1.json")

BOUNDED, SECULAR, EXPONENTIAL = "BOUNDED", "SECULAR", "EXPONENTIAL"

_CERT = None


def cert():
    global _CERT
    if _CERT is None:
        with open(CERT_PATH) as fh:
            _CERT = json.load(fh)
    return _CERT


class TestTheMeasurementSeparates(unittest.TestCase):
    def setUp(self):
        self.by = {r["case"]: r for r in cert()["regimes"]}

    def test_all_checks_pass(self):
        self.assertTrue(cert()["checks"]["ok"])
        self.assertEqual(cert()["checks"]["failures"], [])

    def test_three_distinct_behaviours(self):
        self.assertEqual(
            {r["behaviour"] for r in cert()["regimes"]},
            {BOUNDED, SECULAR, EXPONENTIAL})

    def test_the_two_failure_modes_are_distinguishable(self):
        """If they were not, diagonalizability and reality would be
        operationally the same condition -- and they are not."""
        self.assertNotEqual(self.by["exceptional"]["behaviour"],
                            self.by["unstable"]["behaviour"])

    def test_the_exponential_rate_alone_is_not_enough(self):
        """Bounded and secular share rate zero, so boundedness must be asked
        separately.  This is why the classifier has two stages."""
        self.assertEqual(self.by["harmless"]["exponential_rate"],
                         self.by["exceptional"]["exponential_rate"])

    def test_each_behaviour_is_the_predicted_one(self):
        for r in cert()["regimes"]:
            self.assertTrue(r["matches"], r["case"])


class TestTheVerifiabilityStructure(unittest.TestCase):
    def setUp(self):
        self.by = {r["case"]: r for r in cert()["regimes"]}

    def test_every_regime_is_verifiable_somehow(self):
        for r in cert()["regimes"]:
            self.assertTrue(r["verifiable_by_parameters"]
                            or r["verifiable_by_trajectory"], r["case"])

    def test_no_single_modality_suffices(self):
        self.assertFalse(all(r["verifiable_by_parameters"]
                             for r in cert()["regimes"]))
        self.assertFalse(all(r["verifiable_by_trajectory"]
                             for r in cert()["regimes"]))

    def test_harmlessness_and_the_exceptional_point_need_different_modalities(self):
        h, e = self.by["harmless"], self.by["exceptional"]
        self.assertTrue(h["verifiable_by_parameters"])
        self.assertFalse(h["verifiable_by_trajectory"])
        self.assertFalse(e["verifiable_by_parameters"])
        self.assertTrue(e["verifiable_by_trajectory"])

    def test_openness_matches_nonzero_discriminant(self):
        for r in cert()["regimes"]:
            self.assertEqual(r["openness"]["open"], r["discriminant"] != 0,
                             r["case"])

    def test_every_verdict_gives_a_reason(self):
        for name, v in cert()["verifiability"].items():
            self.assertTrue(v["why_parameters"], name)
            self.assertTrue(v["why_trajectory"], name)


class TestItDoesNotOverclaim(unittest.TestCase):
    def setUp(self):
        with open(CERT_PATH) as fh:
            self.disk = json.load(fh)

    def test_it_says_it_does_not_generalise(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("that the construction generalises", joined)
        self.assertIn("built once", joined)
        self.assertIn("without operational content", joined)

    def test_it_disclaims_their_formal_machinery(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("sigma-algebras are not", joined)

    def test_the_open_row_stays_open(self):
        self.assertIn("C-GHOST-DYNAMICS stays OPEN",
                      " ".join(self.disk["does_not_establish"]))
        with open(os.path.join(
                REPO_ROOT, "reverse_physics", "certificates",
                "REVERSE_PHYSICS_WEYL_VS_EINSTEIN_LEDGER_V1.json")) as fh:
            ledger = json.load(fh)
        row = next(r for r in ledger["rows"] if r["id"] == "C-GHOST-DYNAMICS")
        self.assertEqual(row["status"], "OPEN")

    def test_the_verdicts_are_flagged_as_judgements(self):
        joined = " ".join(self.disk["does_not_establish"]).lower()
        self.assertIn("judgement", joined)

    def test_the_missed_mode_reading_is_recorded(self):
        m = self.disk["the_missed_mode"]
        self.assertIn("scattering_c_factorisation", m["what"])
        self.assertIn("by construction", m["operational_reading"].lower())


if __name__ == "__main__":
    unittest.main()
