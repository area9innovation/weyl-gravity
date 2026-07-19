from __future__ import annotations

import unittest

from d_quotient_classical.relative.einstein_weyl_relative_316_block_diagonal_q2_obstruction import build
from d_quotient_classical.relative.verify_einstein_weyl_relative_316_block_diagonal_q2_obstruction import verify


class Relative316BlockDiagonalQ2ObstructionTest(unittest.TestCase):
    def test_projection_replays_nonzero_taub_witness(self) -> None:
        value = build()
        self.assertEqual(value["projection_argument"]["normalized_nonzero_witness"], "-54*(1 + sqrt(3))/5")
        self.assertTrue(value["projection_argument"]["current_or_cotangent_output_projects_to_zero"])

    def test_only_block_diagonal_full_domain_q2_is_obstructed(self) -> None:
        value = build()
        classification = value["classification"]
        self.assertFalse(classification["complete_full_domain_q2_on_block_diagonal_316_exists"])
        self.assertFalse(classification["derived_taub_zero_homotopy_pullback_obstructed"])
        self.assertFalse(classification["nonzero_typed_unary_cross_incidence_obstructed"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
