"""Fail-closed checks for the fourth transverse curvature-jet layer."""

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_coordinate_curvature_jets import (
    MAX_JET_ORDER,
    orthonormal_covector_jet,
)


def _count(word: tuple[int, ...]) -> int:
    return sum(
        value != 0
        for left in range(4)
        for right in range(4)
        for value in orthonormal_covector_jet(word, left, right)
    )


class NariaiTransverseHighOrderCurvatureJetsTests(unittest.TestCase):
    def test_declared_high_jet_layers_are_nonzero(self) -> None:
        self.assertEqual(MAX_JET_ORDER, 5)
        self.assertEqual(_count((0, 0, 0, 0)), 24)
        self.assertEqual(_count((1, 1, 1, 1)), 24)
        self.assertGreater(_count((0, 0, 0, 0, 0)), 0)

    def test_above_declared_order_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "exceeds certified maximum"):
            orthonormal_covector_jet((0, 0, 0, 0, 0, 0), 0, 1)


if __name__ == "__main__":
    unittest.main()
