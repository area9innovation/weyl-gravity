from __future__ import annotations

import copy
import unittest

from d_quotient_classical.causal_transfer import weak_background_causal_vs_d_stability as theorem


class WeakBackgroundCausalVsDStabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()

    def test_certificate_validates(self) -> None:
        theorem.validate(self.value)

    def test_positive_fixture_keeps_fixed_d_target(self) -> None:
        row = self.value["fixtures"]["positive_conformal_fixture"]
        self.assertEqual(row["sigma_D"], "0")
        self.assertEqual(row["fixed_augmentation_D_Cartan"], "CERTIFIED because sigma_D=0")

    def test_negative_fixture_separates_causal_and_d(self) -> None:
        row = self.value["fixtures"]["negative_conformal_fixture"]
        self.assertEqual(row["causal_complex"], "CERTIFIED")
        self.assertEqual(row["augmentation_equivariance_defect"], "-1/21")
        self.assertEqual(row["fixed_augmentation_D_Cartan"], "OBSTRUCTED")

    def test_finite_residual_gap_fixture(self) -> None:
        row = self.value["fixtures"]["finite_residual_fixture"]
        self.assertEqual(row["neumann_ratio"], "1/2")
        self.assertEqual(row["cartan_defect_rank"], 0)
        self.assertEqual(row["contraction_defect_rank"], 0)
        self.assertEqual(row["weight_crossing_rank"], 2)

    def test_bach_flat_openness_is_relative(self) -> None:
        row = self.value["background_classes"]["bach_flat_nariai_adm"]
        self.assertIn("relative C0 ADM", row["topology"])
        self.assertIn("not ambient-open", row["open_set"])

    def test_ks_slab_does_not_promote_whole_cylinder(self) -> None:
        row = self.value["background_classes"]["conformally_einstein_ks_slabs"]
        self.assertEqual(row["causal_verdict"], "CERTIFIED_ON_EACH_COMMON_SLAB")
        self.assertEqual(row["whole_cylinder_verdict"], "OBSTRUCTED_FOR_THE_DECLARED_NONZERO_BRANCH")

    def test_hadamard_and_quantum_remain_false(self) -> None:
        self.assertFalse(self.value["flags"]["HADAMARD_TRANSFER"])
        self.assertFalse(self.value["flags"]["QUANTUM_CLAIM"])

    def test_mutation_erasing_split_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["flags"]["CAUSAL_STABILITY_IMPLIES_D_CARTAN_STABILITY"] = True
        with self.assertRaises(Exception):
            theorem.validate(mutant)


if __name__ == "__main__":
    unittest.main()
