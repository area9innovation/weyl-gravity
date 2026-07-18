"""Tier-1 tests for the BH-2A horizon-reach certificate.

Both rails are cheap here (~3 s each): the fast rail checks the schema
and flags; the exhaustive rail runs the full independent verifier.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

import verify_bh2a_horizon_reach as vf  # noqa: E402

CERT = json.loads((PKG / "certificates" / "BH2A_HORIZON_REACH.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2a-horizon-reach-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"], "BH2A_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL"
        )
        flags = CERT["claim_flags"]
        self.assertTrue(flags["ingoing_family_dimension_certified"])
        self.assertFalse(flags["flux_or_sign_certified"])
        self.assertFalse(flags["causal_exclusion_decided"])
        self.assertFalse(flags["growth_or_stability_certified"])


class TestExhaustiveRail(unittest.TestCase):
    def test_full_independent_verifier(self):
        vf.verify_certificate()


if __name__ == "__main__":
    unittest.main()
