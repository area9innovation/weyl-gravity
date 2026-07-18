"""Tier-1 tests for the BH-2A causal-disposition certificate."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import jsonschema

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))

import verify_bh2a_causal_disposition as vf  # noqa: E402

CERT = json.loads((PKG / "certificates" / "BH2A_CAUSAL_DISPOSITION.json").read_text())


class TestFastRail(unittest.TestCase):
    def test_schema_verdict_and_flags(self):
        schema = json.loads(
            (PKG / "schema" / "bh2a-causal-disposition-v1.schema.json").read_text()
        )
        jsonschema.Draft202012Validator(schema).validate(CERT)
        self.assertEqual(
            CERT["result_token"], "BH2A_AXIAL_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE"
        )
        flags = CERT["claim_flags"]
        self.assertTrue(flags["no_growing_asymptotics_certified"])
        self.assertTrue(flags["extra_branch_unavoidable_mode_level_certified"])
        self.assertFalse(flags["complex_frequency_structure_certified"])
        self.assertFalse(flags["stability_or_ringdown_certified"])


class TestExhaustiveRail(unittest.TestCase):
    def test_full_independent_verifier(self):
        vf.verify_certificate()


if __name__ == "__main__":
    unittest.main()
