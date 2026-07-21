"""Tier-1 fast rail for the BH-3 numerical-validation protocol specification.

Structural only: schema, verdict, that it is a specification (no numerics),
the pinned real-axis anchors, the independent-rail requirement, and the
fail-closed claim boundary.
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
    (PKG / "certificates" / "BH3_NUMERICAL_VALIDATION_PROTOCOL.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_and_verdict(self):
        schema = json.loads(
            (PKG / "schema"
             / "bh3-numerical-validation-protocol-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"],
                         "BH3_NUMERICAL_VALIDATION_PROTOCOL_SPECIFIED")
        self.assertEqual(CERT["artifact_kind"], "PROTOCOL_SPECIFICATION")
        self.assertEqual(CERT["dependency_tags"],
                         ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])
        self.assertNotIn("LORENTZIAN-CAUSAL", CERT["dependency_tags"])

    def test_specification_only(self):
        d = CERT["declaration"]
        self.assertTrue(d["is_specification_only"])
        self.assertTrue(d["no_computation_run"])
        cf = CERT["claim_flags"]
        for f in ("spectrum_computed", "quasinormal_mode_computed",
                  "off_real_axis_result_established", "numerical_rail_implemented"):
            self.assertFalse(cf[f])

    def test_real_axis_anchors_present(self):
        anc = CERT["protocol"]["real_axis_cross_check_anchors"]
        aa = anc["a_of_omega"]
        self.assertTrue(aa["no_real_poles"])
        self.assertTrue(aa["omega_zero_excluded"])
        self.assertIn("I", aa["poles"])
        self.assertIn("I/2", aa["poles"])
        self.assertTrue(anc["horizon_indicial"]["einstein_rw_exponents"])
        self.assertTrue(anc["infinity_asymptotics"]["exponents"])
        self.assertEqual(anc["exceptional_angular_set"]["exceptional_l"], [0, 1])

    def test_independent_rail_and_fail_closed(self):
        nm = CERT["protocol"]["numerical_method"]
        self.assertIn("independent", nm["independent_rail_requirement"].lower())
        self.assertTrue(nm["method_A"] and nm["method_B"])
        acc = CERT["protocol"]["acceptance_thresholds"]
        self.assertIn("never a pass", acc["fail_closed"].lower())
        cd = CERT["protocol"]["continuation_domain"]["statement"]
        self.assertIn("{i, i/2}", cd)

    def test_no_promotion_vocabulary(self):
        positive = {k: v for k, v in CERT.items()
                    if k not in ("does_not_establish", "missing_objects")}
        blob = json.dumps(positive).lower()
        for banned in ("spectrum computed", "quasinormal mode computed",
                       "ringdown", "stability certified"):
            self.assertNotIn(banned, blob)
        self.assertGreaterEqual(len(CERT["does_not_establish"]), 1)


if __name__ == "__main__":
    unittest.main()
