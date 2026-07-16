from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_all_ell_symplectic_restriction import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_axial_all_ell_symplectic_restriction import (
    verify_certificate as verify_independently,
)


class WeylAxialAllEllSymplecticRestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()

    def test_off_shell_matrix(self) -> None:
        self.assertEqual(
            self.payload["restriction"]["weyl_maxwell_off_shell_coefficient_matrix"],
            [["lambda*(3*mu-3*lambda+1)", "0"], ["0", "2"]],
        )

    def test_all_ell_branch_ratios_and_signature(self) -> None:
        rows = self.payload["restriction"]["on_shell_branches"]
        self.assertEqual(
            [row["restriction_over_einstein"] for row in rows],
            ["3*sqrt(2)*sqrt(lambda)/2 + 1", "-3*sqrt(2)*sqrt(lambda)/2 + 1"],
        )
        self.assertEqual([row["ell_ge_2_relative_sign"] for row in rows], ["POSITIVE", "NEGATIVE"])
        proof = self.payload["restriction"]["ell_ge_2_proof"]
        self.assertEqual(proof["rank"], 2)
        self.assertEqual(
            proof["signature_relative_to_positive_einstein_branch_form"],
            {"positive": 1, "negative": 1, "zero": 0},
        )

    def test_ell1_is_only_a_consistency_control(self) -> None:
        control = self.payload["restriction"]["ell1_consistency_control"]
        self.assertEqual(control["formal_branch_masses"], ["4", "0"])
        self.assertTrue(control["not_an_all_ell_physical_claim"])
        self.assertFalse(self.payload["classification"]["physical_ell1_and_global_twist_restriction_computed"])

    def test_open_blocks_remain_open(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["all_axial_ell_ge2_restriction_computed"])
        for key in (
            "polar_restriction_computed",
            "homogeneous_restriction_computed",
            "complete_fourth_order_weyl_maxwell_phase_space_classified",
            "nonlinear_solution_embedding_certified",
            "final_residual_quotient_computed",
            "lorentzian_causal_or_scattering_theorem",
        ):
            self.assertFalse(classification[key])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
