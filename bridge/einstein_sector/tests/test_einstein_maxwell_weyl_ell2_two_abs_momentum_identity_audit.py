from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class Ell2TwoAbsMomentumIdentityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_identity_audit.json").read_text())

    def test_canonical_audit_has_198_rows(self) -> None:
        self.assertEqual(self.value["canonical_reduction"]["audited_row_count"], 198)
        self.assertEqual(len(self.value["identity_audit"]["rows"]), 198)

    def test_no_identity_resonance_survives(self) -> None:
        self.assertEqual(self.value["identity_audit"]["identity_resonant_row_count"], 0)
        self.assertTrue(self.value["classification"]["no_identity_resonant_channel"])

    def test_both_relative_spatial_signs_are_present(self) -> None:
        signs = {row["relative_spatial_sign"] for row in self.value["identity_audit"]["rows"]}
        self.assertEqual(signs, {-1, 1})

    def test_generic_circumference_only_is_certified(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["generic_circumference_cross_fibre_nonresonance_certified"])
        self.assertFalse(classification["isolated_circumference_source_coefficients_computed"])

    def test_complete_two_fibre_cone_remains_open(self) -> None:
        self.assertFalse(self.value["classification"]["complete_two_fibre_tangent_cone_classified"])
        self.assertIn("same-fibre rows", self.value["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
