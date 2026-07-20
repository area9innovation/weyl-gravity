"""Tier-1 fast rail for the corrected axial composed-lift certificate."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH2A_COMPOSED_REPAIR.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2a-composed-repair-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"],
                         "BH2A_COMPOSED_LIFT_CORRECTED_EXACT_CONSTANT_FLUX")
        flags = CERT["claim_flags"]
        self.assertTrue(flags["corrected_composition_certified"])
        self.assertTrue(flags["rw_gauge_lift_exists"])
        self.assertTrue(flags["exact_constant_flux_certified"])
        self.assertTrue(flags["null_control_exact"])
        self.assertTrue(flags["supersedes_bh2a_cross_flux_values"])
        self.assertFalse(flags["symbolic_omega_certified"])
        self.assertFalse(flags["invariant_sign_theory_certified"])

    def test_exact_values(self):
        fx = CERT["fixtures"]
        self.assertEqual(fx["3/5"]["control"], "0")
        self.assertEqual(fx["3/5"]["ee"], "284488128*I/648125")
        self.assertEqual(fx["2/7"]["ee"], "206883648*I/5908175")
        self.assertEqual(fx["3/5"]["cross"],
                         "-10893744/129625 + 780048*I/25925")
        self.assertEqual(fx["2/7"]["cross"],
                         "-15606912/844025 + 1283712*I/120575")

    def test_supersession_and_defects(self):
        sup = CERT["supersedes"]
        self.assertEqual(sup["certificate"],
                         "black_hole_programme/certificates/BH2A_CROSS_FLUX.json")
        self.assertEqual(len(sup["defects"]), 3)
        for tag in ("D1", "D2", "D3"):
            self.assertTrue(any(d.startswith(tag) for d in sup["defects"]))

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
