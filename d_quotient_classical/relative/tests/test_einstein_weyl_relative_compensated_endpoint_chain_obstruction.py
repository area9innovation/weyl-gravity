#!/usr/bin/env python3
"""Tests for the compensated endpoint flat-symbol obstruction."""

from __future__ import annotations

from copy import deepcopy
import unittest

from jsonschema import ValidationError

from d_quotient_classical.relative import (
    einstein_weyl_relative_compensated_endpoint_chain_obstruction as subject,
)


class CompensatedEndpointChainObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = subject.build()

    def test_exact_obstruction_and_repair(self) -> None:
        subject.validate(self.value)
        obstruction = self.value["flat_polynomial_obstruction"]
        self.assertEqual(
            (obstruction["rank_over_Q"], obstruction["augmented_rank_over_Q"]),
            (3, 4),
        )
        self.assertEqual(
            obstruction["polynomial_elimination"]["normal_form_of_xi"], "xi"
        )
        self.assertFalse(obstruction["polynomial_elimination"]["membership"])
        self.assertEqual(
            self.value["minimal_covariant_symbol_repair"][
                "unique_lowest_degree_solution"
            ],
            {"u": "0", "v": "1/2", "w": "0", "b": "1/2"},
        )

    def test_order_one_regression_is_independent_of_compensation(self) -> None:
        regression = self.value["order_one_original_system_regression"]
        self.assertEqual(regression["witness_matrix_rows"], [[[7, "1"]], [[7, "-1"]]])
        self.assertEqual(regression["left_null_evaluation"], "1")
        self.assertIn("lambda_H=0", regression["reason_compensation_does_not_change_witness"])

    def test_fail_closed_mutations(self) -> None:
        for key in (
            "complete_existing_carrier_unary_chain_lift_exists",
            "obstruction_uses_order_extrapolation",
            "full_chain_map_on_enlarged_carrier_constructed",
            "relative_q2_or_f2_activated",
            "causal_observable_nonlinear_particle_or_quantum_claim",
        ):
            mutant = deepcopy(self.value)
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError, msg=key):
                subject.validate(mutant)


if __name__ == "__main__":
    unittest.main()
