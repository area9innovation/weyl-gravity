"""Tier-1 fast rail for the BH-2A cross-flux certificate.

Exhaustive rail: `verify_bh2a_cross_flux.py` (~5 min: independent
third-frequency pipeline run), executed separately.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

CERT = json.loads((PKG / "certificates" / "BH2A_CROSS_FLUX.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2a-cross-flux-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"], "BH2A_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES")
        flags = CERT["claim_flags"]
        self.assertTrue(flags["extra_norm_nonzero_certified"])
        self.assertTrue(flags["cross_nonzero_certified"])
        self.assertFalse(flags["symbolic_omega_dependence_certified"])
        self.assertFalse(flags["causal_disposition_decided"])
        self.assertFalse(flags["stability_or_ringdown_certified"])

    def test_fixture_internal_consistency(self):
        self.assertEqual(len(CERT["fixtures"]), 2)
        for fx in CERT["fixtures"]:
            ees = [complex(s) for s in fx["ee_over_pi_alpha_float"]]
            ctls = [complex(s) for s in fx["control_over_pi_alpha_float"]]
            crs = [complex(s) for s in fx["cross_over_pi_alpha_float"]]
            for e in ees:
                self.assertLess(abs(e.real), 1e-9 * abs(e))
                self.assertLess(e.imag, 0)
            for c, e in zip(ctls, ees):
                self.assertLess(abs(c), 1e-12 * abs(e))
            self.assertLess(abs(ees[0] - ees[1]), 0.02 * abs(ees[0]))
            for c in crs:
                self.assertGreater(abs(c), abs(ees[0]) / 10)

    def test_frequency_robustness_recorded(self):
        omegas = {fx["omega"] for fx in CERT["fixtures"]}
        self.assertEqual(omegas, {"3/5", "2/7"})


if __name__ == "__main__":
    unittest.main()
