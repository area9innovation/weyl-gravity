"""Tier-1 fast rail for the BH-2C polar flux-class certificate."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
CERT = json.loads(
    (PKG / "certificates" / "BH2C_POLAR_FLUX_CLASS.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2c-polar-flux-class-v1.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH2C_POLAR_NORM_SELECTION_EINSTEIN_SELECTED_AT_INFINITY")
        flags = CERT["claim_flags"]
        self.assertTrue(flags["polar_composed_classes_certified"])
        self.assertTrue(flags["polar_power_enhancement_certified"])
        self.assertTrue(flags["polar_flux_power_table_certified"])
        self.assertTrue(flags["polar_einstein_finite_class_certified"])
        self.assertTrue(flags["polar_extra_divergent_class_certified"])
        self.assertFalse(flags["symbolic_frequency_certified"])
        self.assertFalse(flags["asymptotic_phase_space_constructed"])
        self.assertFalse(flags["norm_sign_certified"])

    def test_class_semantics(self):
        cls = CERT["composed_classes"]["classes"]
        for entry in cls["0"]:
            self.assertEqual(entry[:2], [1, 1])   # enhancement + single log
        for entry in cls["-2w"]:
            self.assertEqual(entry[:2], [0, 0])   # pure oscillatory power

    def test_table_semantics(self):
        t = CERT["flux_table"]
        from fractions import Fraction
        for k, entry in t.items():
            na, nb = k.split("|")
            if na.startswith("E") and nb.startswith("E"):
                # Einstein pairs: slice-integrable (zero or <= r^-2)
                if entry["leading"] is not None:
                    self.assertLessEqual(Fraction(entry["leading"][0]), -2)
            else:
                # every extra-involving pair: certified divergent
                self.assertIsNotNone(entry["leading"])
                self.assertGreaterEqual(Fraction(entry["leading"][0]), 1)
                self.assertGreater(Fraction(entry["leading"][0]),
                                   Fraction(entry["noise_floor"]))

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
