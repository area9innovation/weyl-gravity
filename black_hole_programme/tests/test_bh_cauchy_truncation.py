"""Tier-1 fast rail for the local Einstein Cauchy-truncation certificate."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" /
             "bh-local-einstein-cauchy-truncation-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH_LOCAL_CAUCHY_TRUNCATION_SELECTS_EINSTEIN_MODULO_CONFORMAL_GAUGE")
        flags = CERT["claim_flags"]
        self.assertTrue(flags["axial_cauchy_truncation_certified"])
        self.assertTrue(flags["polar_conformal_obstruction_certified"])
        self.assertTrue(flags["polar_quotient_truncation_certified"])
        self.assertTrue(flags["constraint_propagation_certified"])
        self.assertTrue(flags["exact_sequence_stated_without_splitting"])
        self.assertFalse(flags["nonlinear_or_stability_claim"])
        self.assertFalse(flags["every_psi_lifts_claim"])
        self.assertFalse(flags["sourced_flux_numbers_used"])

    def test_mutation_semantics(self):
        mut = CERT["mutation"]
        self.assertEqual(mut["dropped_datum"], "nabla_n psi|_Sigma")
        self.assertIn("u|_Sigma = 0", mut["witness"])

    def test_boundary_honesty(self):
        self.assertIn("no horizon or finite-radius timelike boundary",
                      CERT["declaration"]["boundary_conditions"])
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
