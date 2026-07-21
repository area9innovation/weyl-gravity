"""Tier-1 fast rail for the BH-3 exterior BVP well-posedness gate."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_and_verdict(self):
        schema = json.loads(
            (PKG / "schema"
             / "bh3-exterior-bvp-wellposedness-gate-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH3_EXTERIOR_BVP_EINSTEIN_WELLPOSED_MODULO_DISCRETE_"
            "ADDITIONAL_LOGTAIL_OBSTRUCTED")
        self.assertEqual(CERT["dependency_tags"],
                         ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])

    def test_bvp_stated(self):
        b = CERT["bvp_definition"]
        for k in ("exterior_domain", "operator", "horizon_condition",
                  "outer_condition"):
            self.assertTrue(str(b[k]).strip())

    def test_einstein_wellposed_modulo_discrete(self):
        eb = CERT["einstein_branch"]
        self.assertIn("log-free", eb["type"])
        self.assertIn("Wronskian", eb["wellposedness_criterion"])
        self.assertIn("discrete", eb["disposition"].lower())

    def test_additional_branch_obstruction(self):
        ab = CERT["additional_branch"]
        self.assertIn("log", ab["type"].lower())
        self.assertIn("ill-defined", ab["first_failed_hypothesis"].lower())
        self.assertIn("outgoing", ab["obstruction"].lower())

    def test_claim_boundary(self):
        cf = CERT["claim_flags"]
        for t in ("bvp_precisely_stated",
                  "einstein_wellposed_modulo_discrete_certified",
                  "additional_branch_obstruction_certified",
                  "einstein_vs_additional_distinguished"):
            self.assertTrue(cf[t])
        for f in ("connection_wronskian_constructed", "exceptional_set_computed",
                  "additional_outgoing_condition_resolved",
                  "discrete_spectrum_claimed", "qnm_stability_scattering_claimed",
                  "single_frequency_solve_used"):
            self.assertFalse(cf[f])
        self.assertGreaterEqual(len(CERT["does_not_establish"]), 1)

    def test_no_promotion_vocabulary(self):
        positive = {k: v for k, v in CERT.items()
                    if k not in ("does_not_establish", "missing_objects")}
        blob = json.dumps(positive).lower()
        for banned in ("quasinormal mode computed", "quasinormal spectrum",
                       "ringdown computed", "stability certified",
                       "scattering matrix"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
