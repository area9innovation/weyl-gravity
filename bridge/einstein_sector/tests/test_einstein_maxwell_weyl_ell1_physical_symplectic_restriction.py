from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_ell1_physical_symplectic_restriction import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell1_physical_symplectic_restriction import (
    verify_certificate as verify_independently,
)


class WeylEll1PhysicalRestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()

    def test_direct_gauge_descent(self) -> None:
        descent = self.payload["theorem"]["direct_gauge_descent"]
        self.assertTrue(descent["both_gauge_rows_and_columns_zero"])
        self.assertEqual(descent["axial_on_shell_target_matrix_raw"][1], ["0", "0"])
        self.assertEqual(descent["polar_on_shell_target_matrix_raw"][1], ["0", "0"])

    def test_factor_four_in_both_parities(self) -> None:
        rows = self.payload["theorem"]["parity_rows"]
        self.assertEqual(rows["axial"]["restriction_over_einstein"], "4")
        self.assertEqual(rows["polar"]["restriction_over_einstein"], "4")
        self.assertEqual(
            self.payload["theorem"]["normalized_direct_sum_theorem"]["relative_operator"],
            [["4", "0"], ["0", "4"]],
        )

    def test_generic_polar_continuation_is_rejected(self) -> None:
        control = self.payload["theorem"]["generic_polar_lambda_to_2_failure"]
        self.assertEqual(control["target_gauge_norm"], "16")
        self.assertEqual(control["target_gauge_physical_cross"], "-24")
        self.assertEqual(control["quotient_representative_naive_ratio"], "2")
        self.assertFalse(self.payload["classification"]["generic_polar_lambda_to_2_continuation_valid"])

    def test_mode_counting_and_global_separation(self) -> None:
        theorem = self.payload["theorem"]
        self.assertEqual(theorem["mode_counting"]["real_phase_space_dimension"], "4*q")
        self.assertTrue(theorem["global_separation"]["physical_ell1_is_radiative"])
        self.assertFalse(theorem["global_separation"]["axial_n0_zero_frequency_twist_included"])

    def test_no_quantum_promotion(self) -> None:
        boundary = self.payload["theorem"]["quantum_norm_boundary"]
        self.assertFalse(boundary["positive_frequency_complex_structure_constructed"])
        self.assertFalse(boundary["one_particle_norm_certified"])
        self.assertFalse(boundary["ghost_or_unitarity_theorem"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
