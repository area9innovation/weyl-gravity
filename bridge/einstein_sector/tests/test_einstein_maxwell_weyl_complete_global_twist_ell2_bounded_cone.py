"""Tests for the complete standard-global/twist plus ell=2 bounded cone."""

from __future__ import annotations

import json
import unittest

from bridge.einstein_sector import einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone as theorem


class CompleteGlobalTwistEll2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()

    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(theorem.OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_union_is_complete(self) -> None:
        self.assertTrue(self.value["complete_bounded_zero_locus"]["union_is_necessary_and_sufficient"])

    def test_static_stratum_retains_only_static_moduli(self) -> None:
        static = self.value["complete_bounded_zero_locus"]["static_stratum"]
        self.assertIn("a=b=Q_e=B=0", static)
        self.assertIn("c,d,W_x,A arbitrary", static)

    def test_wave_stratum_removes_dynamical_globals(self) -> None:
        wave = self.value["complete_bounded_zero_locus"]["wave_stratum"]
        self.assertIn("a=b=d=Q_e=B=0", wave)
        self.assertIn("c,W_x,A arbitrary", wave)
        self.assertIn("mu_H=mu_J1=mu_J2=mu_J3=0", wave)

    def test_radion_gate_is_all_m_and_both_parities(self) -> None:
        audit = self.value["radion_audit"]
        self.assertEqual(audit["m0_exact_ideals"]["axial"], "<b*z,a*z,d*z>")
        self.assertEqual(audit["m0_exact_ideals"]["polar"], "<b*z,a*z,d*z>")
        self.assertIn("every m", audit["SO3_promotion"])

    def test_electric_gate_uses_independent_E11_row(self) -> None:
        audit = self.value["electric_audit"]
        self.assertEqual(audit["pure_electric_source"], ["-Q_e**2/2", "Q_e**2/2", "-Q_e**2/2", "0"])
        self.assertEqual(audit["wave_scalar_row_direction"][1], "0")
        self.assertIn("E11=Q_e^2/2", audit["consequence"])

    def test_higher_lifecycles_remain_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["other_ell_or_nonzero_momentum_classified"])
        self.assertFalse(classification["unrestricted_smooth_secular_cone_classified"])
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
