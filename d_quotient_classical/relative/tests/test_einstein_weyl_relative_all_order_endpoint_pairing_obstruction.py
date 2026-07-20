from __future__ import annotations

import unittest

from d_quotient_classical.relative import (
    einstein_weyl_relative_all_order_endpoint_pairing_obstruction as theorem,
)


class AllOrderEndpointPairingObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()
        theorem.validate(cls.value)

    def test_fixed_endpoint_is_obstructed_without_order_extrapolation(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(
            classification[
                "fixed_diffeomorphism_only_endpoint_obstructed_at_all_finite_orders"
            ]
        )
        self.assertFalse(classification["all_order_statement_uses_order_extrapolation"])
        self.assertEqual(
            self.value["formal_pairing_theorem"]["differential_order_bound"],
            "none",
        )

    def test_nonconstant_raw_gram_witness(self) -> None:
        witness = self.value["diffeomorphism_only_endpoint"][
            "normalized_nonconstant_witness"
        ]
        self.assertEqual(witness["B0_XY"], "sin(theta)**2")
        self.assertEqual(witness["d_B0_XY"], "2*sin(theta)*cos(theta)*dtheta")

    def test_correlated_maxwell_compensator_is_minimal_but_not_a_chain_map(self) -> None:
        repair = self.value["minimal_repair"]
        self.assertEqual(repair["new_target_rows"], 0)
        self.assertEqual(repair["existing_row_used"], "lambda_cov_star")
        self.assertFalse(repair["complete_corrected_chain_map_constructed"])
        self.assertEqual(
            self.value["correlated_maxwell_compensator"]["corrected_gram"],
            [
                ["-1", "0", "0", "0", "0"],
                ["0", "1", "0", "0", "0"],
                ["0", "0", "1", "0", "0"],
                ["0", "0", "0", "1", "0"],
                ["0", "0", "0", "0", "1"],
            ],
        )


if __name__ == "__main__":
    unittest.main()
