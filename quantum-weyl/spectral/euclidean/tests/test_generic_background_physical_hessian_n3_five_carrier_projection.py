from __future__ import annotations

from copy import deepcopy
import json
import unittest

from spectral.euclidean.generic_background_physical_hessian_n3_five_carrier_projection import (
    DERIVATIVE_ORDERS,
    OUTPUT,
    validate,
)
from spectral.euclidean.verify_generic_background_physical_hessian_n3_five_carrier_projection import (
    verify,
)


class GenericBackgroundPhysicalHessianN3FiveCarrierProjectionTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_laurent_grading_and_exact_rows(self) -> None:
        self.assertEqual(len(self.value["projection_rows"]), 11)
        for row in self.value["projection_rows"]:
            self.assertEqual(row["box_denominator_exponents"], [1, 1, 1])
            self.assertEqual(
                row["numerator_box_degree"],
                6 - DERIVATIVE_ORDERS[row["carrier_id"]] // 2,
            )
            self.assertEqual(row["term_count"], len(row["terms"]))

    def test_degree_six_unisolvence(self) -> None:
        certificate = self.value["interpolation_certificate"]
        self.assertEqual(certificate["training_fixture_count"], 28)
        self.assertEqual(certificate["maximum_box_monomial_count"], 28)
        self.assertEqual(
            certificate["degree_six_box_evaluation_rank_mod_prime"], 28
        )

    def test_fail_closed_physical_boundary(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"])
        self.assertFalse(flags["PHYSICAL_N3_TRIANGLE_INTEGRATED"])
        self.assertFalse(flags["CURVATURE_SQUARED_H2_IMPORTED"])
        self.assertFalse(flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_denominator_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["projection_rows"][0]["box_denominator_exponents"] = [0, 0, 0]
        with self.assertRaises(Exception):
            validate(mutant)

    def test_formula_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["projection_rows"][0]["terms"][0]["coefficient"][
            "numerator"
        ] += 1
        with self.assertRaises(Exception):
            validate(mutant)

    def test_fast_independent_verifier_rail(self) -> None:
        self.assertEqual(verify(self.value, replay_unseen=False), self.value)


if __name__ == "__main__":
    unittest.main()
