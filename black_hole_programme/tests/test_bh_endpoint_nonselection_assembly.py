"""Tier-1 fast rail for the BH endpoint-selection assembly."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH_ENDPOINT_NONSELECTION_ASSEMBLY.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_and_verdict(self):
        schema = json.loads(
            (PKG / "schema"
             / "bh-endpoint-nonselection-assembly-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH_ONE_ENDED_ENDPOINT_SELECTION_INFINITY_EINSTEIN_HORIZON_NONSELECTION")
        self.assertEqual(CERT["dependency_tags"],
                         ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])

    def test_invariant_pairing(self):
        ip = CERT["invariant_pairing"]
        self.assertEqual(ip["rank"], 2)
        self.assertEqual(ip["signature"], "(1, 1)")
        self.assertTrue(ip["det_strictly_negative_real_omega_nonzero"])
        self.assertTrue(ip["cross_nonzero_all_real_omega"])
        self.assertIn("-|a|^2", ip["det"])

    def test_endpoint_disposition(self):
        ed = CERT["endpoint_disposition"]
        self.assertTrue(ed["additional_solution_admitted_at_horizon"])
        self.assertTrue(ed["einstein_forced_on_finite_flux_phase_space"])
        self.assertIn("omega = 0", ed["exceptional_set"])
        self.assertEqual(
            CERT["horizon_nonselection"]["einstein_rw_ingoing_dimension"], 1)

    def test_missing_object_and_cauchy_separation(self):
        self.assertIn("connection",
                      CERT["missing_analytic_object"]["object"].lower())
        self.assertIn("Heun", CERT["missing_analytic_object"]["nature"])
        self.assertTrue(CERT["separation_from_cauchy_truncation"]["distinct"])
        self.assertGreaterEqual(
            len(CERT["counterexample_mutations_rejected"]), 1)

    def test_claim_boundary(self):
        cf = CERT["claim_flags"]
        for t in ("invariant_pairing_rank_signature_certified",
                  "horizon_nonselection_certified", "infinity_selection_certified",
                  "endpoint_disposition_certified", "cauchy_separation_certified",
                  "polar_fixture_only_preserved"):
            self.assertTrue(cf[t])
        for f in ("global_connection_map_constructed",
                  "two_ended_scattering_map_certified",
                  "polar_theorem_beyond_fixture_certified",
                  "qnm_stability_scattering_claimed", "parity_complete_claim"):
            self.assertFalse(cf[f])

    def test_no_promotion_vocabulary(self):
        positive = {k: v for k, v in CERT.items()
                    if k not in ("does_not_establish", "missing_objects")}
        blob = json.dumps(positive).lower()
        for banned in ("quasinormal", "ringdown", "stability certified",
                       "scattering matrix certified", "ghost"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
