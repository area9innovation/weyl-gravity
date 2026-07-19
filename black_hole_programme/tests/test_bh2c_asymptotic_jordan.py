"""Tier-1 fast rail for the BH-2C asymptotic-Jordan certificate.

Exhaustive rail: `verify_bh2c_asymptotic_jordan.py` (~10 min, independent
VbGeo engine), run separately.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

CERT = json.loads((PKG / "certificates" / "BH2C_ASYMPTOTIC_JORDAN.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2c-asymptotic-jordan-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"],
                         "BH2C_ASYMPTOTIC_FORMAL_SYSTEM_LOG_FREE_BOTH_PARITIES")
        flags = CERT["claim_flags"]
        self.assertTrue(flags["axial_log_free_certified"])
        self.assertTrue(flags["polar_mu0_log_free_certified"])
        self.assertTrue(flags["polar_mu2w_log_free_fixture_certified"])
        self.assertFalse(flags["polar_mu2w_symbolic_certified"])
        self.assertFalse(flags["metric_reconstruction_certified"])
        self.assertFalse(flags["finite_flux_boundary_class_certified"])

    def test_tables(self):
        ax = CERT["axial"]
        self.assertTrue(all(v["log_free"] for v in ax.values()))
        self.assertEqual(sorted(ax["0"]["sigma_roots"]), sorted(["0", "-1"]))
        po = CERT["polar"]
        for v in po.values():
            self.assertEqual(v["tail_kernel"], 3)
            self.assertEqual(v["log_free"], 3)

    def test_vocabulary(self):
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
