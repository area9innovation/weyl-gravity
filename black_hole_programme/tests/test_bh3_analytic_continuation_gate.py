"""Tier-1 fast rail for the BH-3 analytic-continuation gate.

Structural only (the heavy symbolic re-derivation is the verifier's job):
schema, verdict, exact axial singular sets, declared pole-excluding domain,
polar NOT_ACTIVATED, and the fail-closed claim boundary.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH3_ANALYTIC_CONTINUATION_GATE.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_and_verdict(self):
        schema = json.loads(
            (PKG / "schema"
             / "bh3-analytic-continuation-gate-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH3_AXIAL_ANALYTIC_CONTINUATION_MEROMORPHIC_POLAR_NOT_ACTIVATED")
        self.assertEqual(CERT["dependency_tags"],
                         ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])

    def test_axial_exact_singular_set(self):
        cc = CERT["axial_analytic_continuation"]["cross_current"]
        self.assertTrue(cc["is_rational_no_branch_points"])
        self.assertEqual(sorted(cc["pole_set_exact"]), ["I", "I/2"])
        self.assertIn("0", cc["zero_set_exact"])
        mf = CERT["axial_analytic_continuation"]["mode_families"]
        self.assertTrue(mf["boundary_exponents_entire_in_omega"])
        self.assertEqual(mf["infinity_series_omega_poles"], ["0"])

    def test_declared_domain_excludes_poles(self):
        dd = CERT["axial_analytic_continuation"]["declared_domain"]
        self.assertEqual(dd["strip_halfwidth"], "1/4")
        self.assertTrue(dd["real_axis_in_domain"])
        self.assertFalse(dd["continuation_through_pole"])
        self.assertTrue(dd["omega_zero_excluded"])
        self.assertIn("{i, i/2}", dd["current_domain"])

    def test_polar_not_activated(self):
        pd = CERT["polar_disposition"]
        self.assertEqual(pd["status"], "NOT_ACTIVATED")
        self.assertIn("route", pd["route_b_missing_object"].lower() + "route")

    def test_claim_boundary(self):
        cf = CERT["claim_flags"]
        for t in ("axial_current_meromorphic_continuation_certified",
                  "axial_current_exact_singular_set_certified",
                  "no_branch_points_axial_certified",
                  "domain_declared_excludes_poles"):
            self.assertTrue(cf[t])
        for f in ("polar_continuation_activated",
                  "polar_route_b_identity_obtained", "summability_certified",
                  "general_l_certified", "stability_qnm_scattering_claimed"):
            self.assertFalse(cf[f])
        self.assertGreaterEqual(len(CERT["does_not_establish"]), 1)

    def test_no_promotion_vocabulary(self):
        positive = {k: v for k, v in CERT.items()
                    if k not in ("does_not_establish", "missing_objects")}
        blob = json.dumps(positive).lower()
        for banned in ("quasinormal mode computed", "ringdown",
                       "stability certified", "spectrum computed"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
