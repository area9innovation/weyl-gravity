"""Tier-1 fast rail for the BH-2B polar-split certificate.

Exhaustive rail: `verify_bh2b_polar_split.py` (~2 min), run separately.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

CERT = json.loads((PKG / "certificates" / "BH2B_POLAR_SPLIT.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2b-polar-split-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(CERT["result_token"], "BH2B_GENERAL_BRANCH_SPLIT_IDENTITY_CLASSIFIED")
        self.assertEqual(CERT["identity"]["constants"],
                         {"box_ric": "1/2", "weyl_coupling": "1",
                          "grad_grad_R": "-1/6", "g_box_R": "-1/12"})
        flags = CERT["claim_flags"]
        self.assertTrue(flags["general_split_identity_certified"])
        self.assertFalse(flags["zerilli_benchmark_certified"])
        self.assertFalse(flags["polar_causal_disposition_decided"])
        self.assertFalse(flags["stability_or_ringdown_certified"])


if __name__ == "__main__":
    unittest.main()
