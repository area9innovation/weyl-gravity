from __future__ import annotations

from copy import deepcopy
import unittest

from spectral.euclidean.generic_background_physical_hessian_n3_triangle_fixture import (
    build,
    validate,
)
from spectral.euclidean.verify_generic_background_physical_hessian_n3_triangle_fixture import (
    verify,
)


class GenericBackgroundPhysicalHessianN3TriangleFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_formal_adjoint_completion_and_negative_control(self) -> None:
        check = self.value["exact_interior_fixture"]["formal_adjoint_check"]
        self.assertEqual(check["completed_vertex_defect_count"], 0)
        self.assertEqual(check["uncompleted_seed_defect_count"], 62)

    def test_exact_nonzero_triangle_value(self) -> None:
        fixture = self.value["exact_interior_fixture"]
        self.assertEqual(fixture["Delta"], {"numerator": 104, "denominator": 45})
        self.assertEqual(
            fixture["common_Delta_minus4_numerator"],
            {"numerator": -3532544138843839, "denominator": 11210083593750},
        )
        self.assertEqual(
            fixture["kernel_without_(4pi)^-2"],
            {"numerator": -3532544138843839, "denominator": 319810083840000},
        )

    def test_rank_nine_trace_and_all_wick_orders(self) -> None:
        fixture = self.value["exact_interior_fixture"]
        self.assertEqual(fixture["loop_trace"]["matrix_rank"], 9)
        self.assertEqual(fixture["loop_trace"]["maximum_loop_degree"], 6)
        self.assertEqual(fixture["loop_trace"]["monomial_count"], 210)
        self.assertEqual(
            [row["loop_metric_pair_count"] for row in fixture["wick_rows"]],
            [0, 1, 2, 3],
        )

    def test_source_coefficient_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["scalar_flat_momentum_vertex"]["source_seed_rows"][0][
            "coefficient"
        ] = {"numerator": -5, "denominator": 3}
        with self.assertRaises(Exception):
            verify(mutant, reproduce=False)

    def test_wick_contribution_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["exact_interior_fixture"]["wick_rows"][2][
            "raw_wick_contraction"
        ]["numerator"] += 1
        with self.assertRaises(Exception):
            verify(mutant, reproduce=False)

    def test_trace_log_sign_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["parametric_formula"]["physical_trace_log_multiplier"] = {
            "numerator": -1,
            "denominator": 6,
        }
        with self.assertRaises(Exception):
            validate(mutant)

    def test_complete_form_factor_overclaim_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"] = True
        with self.assertRaises(Exception):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        # The standalone verifier performs the expensive second construction.
        # The unit rail reuses the class fixture so its mutation loop remains
        # below the repository's fast-test threshold.
        self.assertEqual(verify(self.value, reproduce=False), self.value)


if __name__ == "__main__":
    unittest.main()
