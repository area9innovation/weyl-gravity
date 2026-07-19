from __future__ import annotations

import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate import build


class TwistAlignedOppositeMomentumGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_common_zero_and_twist_conditions_hold(self) -> None:
        witness = self.value["exact_intersection_witness"]
        self.assertEqual(set(witness["five_moment_maps"].values()), {"0", "0 because the +k and -k branch densities are equal", "0 on the m_A=0 rank-one density"})
        self.assertIn("m_A=0", witness["twist_wave_bounded_column"])

    def test_universal_p_shell_is_populated(self) -> None:
        output = self.value["exact_intersection_witness"]["resonant_output"]
        self.assertEqual(output["target_p_remainder"], "0")
        self.assertEqual(output["target"], "polar extra p-primary")
        self.assertIn("c_minus", output["phase_carrier"])

    def test_bounded_gate_remains_open(self) -> None:
        disposition = self.value["logical_disposition"]
        self.assertTrue(disposition["phase_resonance_divisor_populated"])
        self.assertFalse(disposition["dynamical_adjoint_projection_computed"])
        self.assertEqual(self.value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OPEN")

    def test_smooth_gate_is_imported_without_causal_promotion(self) -> None:
        self.assertEqual(self.value["correction_classes"]["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"], "CERTIFIED")
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
