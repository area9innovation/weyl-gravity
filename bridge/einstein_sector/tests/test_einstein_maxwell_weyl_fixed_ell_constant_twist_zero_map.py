from __future__ import annotations

import unittest

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map import build


class FixedEllConstantTwistZeroMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_every_multiplicity_matrix_is_zero(self) -> None:
        matrices = self.value["multiplicity_matrices"]
        self.assertEqual(sp.Matrix(matrices["Q_(ell,-)"]["matrix"]), sp.zeros(2))
        self.assertEqual(sp.Matrix(matrices["Q_(ell,+)"]["matrix"]), sp.zeros(2))
        self.assertEqual(sp.Matrix(matrices["P_ell"]["matrix"]), sp.zeros(4))

    def test_primary_derivatives_vanish_at_rest(self) -> None:
        theorem = self.value["flat_connection_reduction"]["primary_derivative"]
        derivatives = theorem["k0_derivatives"]
        self.assertEqual(derivatives, {"p": "0", "q": "0"})
        self.assertEqual(theorem["matrix_gram_checks"]["q"]["shell_remainder_rank"], 0)
        self.assertEqual(theorem["matrix_gram_checks"]["p"]["shell_remainder_rank"], 0)

    def test_ell2_direct_replay_is_calibration(self) -> None:
        calibration = self.value["direct_calibration"]
        self.assertTrue(calibration["matches_structural_theorem"])
        self.assertEqual(calibration["Einstein_plus_minus"], "zero")
        self.assertEqual(calibration["extra"], "zero")

    def test_bounded_gate_remains_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["bounded_fixed_ell_constant_twist_cone_complete"])
        self.assertEqual(self.value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OPEN")

    def test_causal_gate_is_not_promoted(self) -> None:
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
