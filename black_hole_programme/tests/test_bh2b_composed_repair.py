"""Tier-1 fast rail for the polar composed-repair certificate."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH2B_COMPOSED_REPAIR.json").read_text())

FAMS = ("E", "G", "X0", "X1", "X2")
CONTROLS = {f"{a}|{b}" for a in FAMS for b in FAMS
            if a == "G" or b == "G" or (a == "E" and b == "E")}


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2b-composed-repair-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"],
                         "BH2B_POLAR_COMPOSED_LIFT_AUDITED_EXACT_CONSTANT_FLUX")
        flags = CERT["claim_flags"]
        for key in ("exact_constant_flux_certified", "all_carrier_modes_lift",
                    "invariance_classified", "vv_vr_audit_complete",
                    "e0_row_superseded", "einstein_selection_confirmed"):
            self.assertTrue(flags[key], key)
        for key in ("symbolic_omega_certified", "general_l_certified",
                    "invariant_sign_theory_certified"):
            self.assertFalse(flags[key], key)

    def test_fixtures_are_exact_and_control_free(self):
        for tag in ("3/5", "2/7"):
            fx = CERT["fixtures"][tag]
            # controls are absent (identically zero, not recorded as values)
            for key in fx:
                self.assertNotIn(key, CONTROLS,
                                 f"control pair {key} recorded as nonzero")
            # every recorded constant is an exact expression, never a float
            for key, val in fx.items():
                self.assertNotIn(".", val.replace("*I", ""),
                                 f"{tag} {key} looks like a float: {val}")
            # 5x5 minus 10 control entries (9 gauge + E|E) = 15 physical pairs
            self.assertEqual(len(fx), 15, tag)

    def test_constancy_window_and_mutations(self):
        win = CERT["constancy_window"]
        self.assertTrue(win["all_zero"])
        self.assertEqual(win["checked_keys"], "1..7")
        self.assertIn("M1_row_audit", CERT["mutations"])
        self.assertIn("(2r+3)/r^2", CERT["mutations"]["M1_row_audit"])
        self.assertTrue(CERT["mutations"]["M2_window"])

    def test_audit_supersedes_e0_row(self):
        audit = CERT["audit"]
        self.assertEqual(audit["e0true_class"], "(-2, 0)")
        self.assertTrue(audit["m2w_clean"])
        self.assertEqual(len(audit["einstein_combination"]), 3)
        # all three mu0 jets have a nonzero vv residual
        for s0 in ("1", "0", "-1"):
            self.assertTrue(audit["vv_residuals"][s0], s0)
        sup = CERT["supersedes"]
        self.assertIn("BH2C_POLAR_FLUX_CLASS.json", sup["flux_class_certificate"])
        self.assertIn("BH2B_POLAR_CROSS_FLUX.json", sup["cross_flux_certificate"])

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal", "stability"):
            self.assertNotIn(banned, blob, banned)


if __name__ == "__main__":
    unittest.main()
