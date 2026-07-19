"""Tier-1 fast rail for the BH-2 omega = 0 static-sector certificate.

Exhaustive rail: `verify_bh2_omega_zero.py` (~10 s, independent VbGeo
engine), run separately.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

CERT = json.loads((PKG / "certificates" / "BH2_OMEGA_ZERO.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2-omega-zero-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"],
                         "BH2_OMEGA_ZERO_STATIC_SECTOR_CLASSIFIED")
        flags = CERT["claim_flags"]
        self.assertTrue(flags["axial_static_sector_classified"])
        self.assertTrue(flags["polar_static_sector_classified"])
        self.assertFalse(flags["static_metric_composition_certified"])
        self.assertFalse(flags["static_flux_or_charge_certified"])

    def test_classification_contents(self):
        c = CERT["classification"]
        self.assertEqual(c["axial_carrier"]["jordan"]["0"], {"alg": 3, "geo": 2})
        self.assertEqual(c["axial_carrier"]["analytic_families"]["0"],
                         {"base_dim": 2, "logfree_dirs": 2})
        self.assertEqual(c["polar_carrier_sliced"]["jordan"]["0"],
                         {"alg": 3, "geo": 3})
        self.assertEqual(
            c["polar_carrier_sliced"]["analytic_families"]["0"]["logfree_dirs"], 1)
        self.assertEqual(
            c["polar_carrier_sliced"]["analytic_families"]["1"]["logfree_dirs"], 1)
        self.assertEqual(c["polar_einstein"]["spectrum"],
                         "PARAMETRIZATION_DEGENERATES")

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
