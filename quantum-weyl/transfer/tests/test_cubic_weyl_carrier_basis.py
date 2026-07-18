from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from transfer.cubic_weyl_carrier_basis import build, validate
from transfer.verify_cubic_weyl_carrier_basis import verify


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class CubicWeylCarrierBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_chiral_block_enumeration_is_exhaustive(self) -> None:
        block = self.value["chiral_block_enumeration"]
        self.assertEqual(block["raw_complete_contractions"], 15)
        self.assertEqual(block["signed_identical_factor_orbits"], 3)
        self.assertEqual(block["tracefree_zero_orbits"], 2)
        self.assertEqual(block["canonical_nonzero_orbits"], 1)

    def test_mixed_chiral_allocations_vanish(self) -> None:
        allocation = self.value["chirality_allocation"]
        self.assertEqual(allocation["mixed_allocations_zero"], 2)
        self.assertEqual(allocation["nonzero_chiral_dimension"], 2)

    def test_parity_basis_has_one_even_and_one_odd_carrier(self) -> None:
        carriers = self.value["tensor_carriers"]
        self.assertEqual(carriers["parity_dimensions"], {"even": 1, "odd": 1})
        self.assertEqual(
            [_fraction(item) for item in carriers["even_coordinate_in_schouten_zero_weyl_image"]],
            [Fraction(2, 3)],
        )

    def test_chiral_and_parity_crosswalks_are_inverse(self) -> None:
        crosswalk = self.value["chiral_parity_crosswalk"]
        left = [[_fraction(item) for item in row] for row in crosswalk["chiral_from_parity"]]
        right = [[_fraction(item) for item in row] for row in crosswalk["parity_from_chiral"]]
        product = [
            [sum((left[i][k] * right[k][j] for k in range(2)), Fraction()) for j in range(2)]
            for i in range(2)
        ]
        self.assertEqual(product, [[1, 0], [0, 1]])

    def test_independence_witness_has_exact_rank_two(self) -> None:
        witness = self.value["independence_witness"]
        matrix = [[_fraction(item) for item in row] for row in witness["evaluation_matrix"]]
        self.assertNotEqual(matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0], 0)
        self.assertEqual(witness["rank"], 2)

    def test_form_factor_and_q1_promotions_fail_closed(self) -> None:
        for flag in (
            "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED",
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
            "RESIDUAL_TRANSFER_AUTHORIZED",
        ):
            mutation = deepcopy(self.value)
            mutation["claim_flags"][flag] = True
            with self.assertRaises(Exception):
                validate(mutation)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.value)


if __name__ == "__main__":
    unittest.main()
