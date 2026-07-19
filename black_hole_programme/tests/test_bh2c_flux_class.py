"""Tier-1 fast rail for the BH-2C flux-class certificate."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads((PKG / "certificates" / "BH2C_FLUX_CLASS.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2c-flux-class-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH2C_FINITE_FLUX_BOUNDARY_CLASS_EINSTEIN_SELECTED_AT_INFINITY")
        flags = CERT["claim_flags"]
        self.assertTrue(flags["composed_log_tails_certified"])
        self.assertTrue(flags["einstein_finite_class_certified"])
        self.assertTrue(flags["extra_divergent_class_certified"])
        self.assertFalse(flags["symbolic_frequency_certified"])
        self.assertFalse(flags["polar_table_certified"])
        self.assertFalse(flags["asymptotic_phase_space_constructed"])

    def test_table_semantics(self):
        t = CERT["flux_table"]
        self.assertLess(int(t["E0|E0"][0]), -1)
        self.assertLess(int(t["E2|E2"][0]), -1)
        for k in ("E0|X0", "X0|X0", "E2|X2", "X2|X2"):
            self.assertGreaterEqual(int(t[k][0]), 0)

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
