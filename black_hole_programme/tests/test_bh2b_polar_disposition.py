"""Tier-1 fast rail for the BH-2B polar disposition certificate.

Exhaustive rail: `verify_bh2b_polar_disposition.py` (~1 min, independent
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

CERT = json.loads((PKG / "certificates" / "BH2B_POLAR_DISPOSITION.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2b-polar-disposition-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"],
            "BH2B_POLAR_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE",
        )
        flags = CERT["claim_flags"]
        self.assertTrue(flags["dispersion_certified"])
        self.assertTrue(flags["no_growing_asymptotics_certified"])
        self.assertTrue(flags["bh2_polar_mode_level_closed"])
        self.assertFalse(flags["complex_frequency_certified"])
        self.assertFalse(flags["well_posedness_certified"])
        self.assertFalse(flags["growth_or_stability_certified"])

    def test_sigma_spectra_recorded(self):
        sig = CERT["asymptotics"]["sigma_ef"]
        self.assertEqual(sig["0"], ["-1", "-2", "-3"])
        self.assertEqual(sorted(sig["-2*omega"]),
                         sorted(["-4*I*omega - 1", "-4*I*omega - 2",
                                 "-4*I*omega - 3"]))

    def test_dependency_tags_and_vocabulary(self):
        self.assertEqual(CERT["dependency_tags"], ["LOCAL-ALGEBRAIC", "REDUCED-MODE"])
        self.assertEqual(CERT["declaration"]["lifecycle"], "CLASSIFIED")
        blob = json.dumps(CERT).lower()
        for banned in ("ringdown", "quasinormal"):
            self.assertNotIn(banned, blob)


if __name__ == "__main__":
    unittest.main()
