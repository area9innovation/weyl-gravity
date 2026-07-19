"""Tests for the complete constant-twist plus ell2 bounded cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone import OUTPUT, build


class ConstantTwistEll2CompleteBoundedConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_resonance_and_moment_equations_are_jointly_complete(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["simultaneous_moment_and_all_branch_resonance_zero_locus_classified"])
        self.assertTrue(classification["bounded_zero_locus_necessary_and_sufficient"])

    def test_nonresonant_outputs_are_exhausted(self) -> None:
        self.assertEqual(set(self.value["nonresonant_output_ledger"]), {"minus", "extra", "plus"})
        for shell in self.value["nonresonant_output_ledger"].values():
            self.assertEqual(set(shell), {"L1", "L3"})
            self.assertIn("exceptional", shell["L1"]["operator_scope"])
            self.assertIn("(1,1,p,pq)", shell["L3"]["operator_scope"])

    def test_quadratic_noether_compatibility_is_explicit(self) -> None:
        noether = self.value["quadratic_Noether_compatibility"]
        self.assertTrue(noether["axial_and_polar_ungauged_complexes_imported"])
        self.assertIn("DE[u]=0", noether["on_shell_reduction"])

    def test_off_axis_survivor_is_present(self) -> None:
        witness = self.value["independence_witnesses"]["off_axis_survivor"]
        self.assertEqual(witness["spin_moments"], ["0", "0", "0"])
        self.assertEqual(witness["energy_remainder"], "0")

    def test_scope_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["twist_velocity_or_other_global_tangents_classified"])
        self.assertFalse(classification["other_ell_or_nonzero_momentum_classified"])
        self.assertFalse(classification["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
