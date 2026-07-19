from __future__ import annotations

import json
import unittest

from bridge.einstein_sector import einstein_maxwell_weyl_complete_global_twist_finite_harmonic_k0_bounded_cone as theorem


class CompleteGlobalTwistFiniteHarmonicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(theorem.OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_finite_additivity_is_explicit(self) -> None:
        proof = self.value["finite_additivity_proof"]
        self.assertIn("sum_ell D2E[A,u_ell]", proof["mixed_source_identity"])
        self.assertIn("linearity of L", proof["overlapping_output_channels"])

    def test_complete_stratified_union(self) -> None:
        locus = self.value["complete_bounded_zero_locus"]
        self.assertTrue(locus["union_is_necessary_and_sufficient"])
        self.assertIn("c,d,W_x,A arbitrary", locus["static_stratum"])
        self.assertIn("c,W_x,A arbitrary", locus["wave_stratum"])
        self.assertIn("total mu_H=mu_J1=mu_J2=mu_J3=0", locus["wave_stratum"])

    def test_multi_ell_twist_column_is_closed(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["finite_multi_ell_constant_twist_column_classified"])
        self.assertTrue(classification["constant_twist_position_free_on_finite_wave_stratum"])
        self.assertTrue(classification["bounded_zero_locus_necessary_and_sufficient"])

    def test_larger_scopes_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["infinite_harmonic_completion_classified"])
        self.assertFalse(classification["nonzero_momentum_classified"])
        self.assertFalse(classification["exceptional_wave_inputs_classified"])
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
