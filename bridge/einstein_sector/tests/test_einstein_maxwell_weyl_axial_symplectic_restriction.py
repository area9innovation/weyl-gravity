from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_symplectic_restriction import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_axial_symplectic_restriction import (
    verify_certificate as verify_independently,
)


class WeylAxialSymplecticRestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()

    def test_all_direct_controls_pass(self) -> None:
        self.assertTrue(all(self.payload["controls"].values()))

    def test_two_exact_branch_ratios(self) -> None:
        rows = self.payload["restriction"]["on_shell_branches"]
        self.assertEqual([row["restriction_over_einstein"] for row in rows], ["1 + 3*sqrt(3)", "1 - 3*sqrt(3)"])
        self.assertEqual([row["relative_sign"] for row in rows], ["POSITIVE", "NEGATIVE"])

    def test_restriction_is_nonnull_but_not_universally_proportional(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["axial_ell2_both_physical_branches_nonnull"])
        self.assertTrue(classification["axial_ell2_restriction_nondegenerate"])
        self.assertFalse(classification["single_universal_proportionality_to_einstein_form"])
        self.assertTrue(classification["relative_branch_form_indefinite"])

    def test_target_gauge_is_not_the_explanation(self) -> None:
        self.assertFalse(self.payload["classification"]["target_weyl_gauge_removes_einstein_class"])

    def test_uncomputed_blocks_remain_open(self) -> None:
        classification = self.payload["classification"]
        for key in (
            "all_axial_ell_ge2_restriction_computed",
            "polar_restriction_computed",
            "global_restriction_computed",
            "nonlinear_solution_embedding_certified",
            "final_residual_quotient_computed",
            "lorentzian_causal_or_scattering_theorem",
        ):
            self.assertFalse(classification[key])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
