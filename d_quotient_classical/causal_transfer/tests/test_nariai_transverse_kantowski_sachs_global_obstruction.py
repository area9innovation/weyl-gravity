from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_kantowski_sachs_global_obstruction import build, validate
from d_quotient_classical.causal_transfer.verify_nariai_transverse_kantowski_sachs_global_obstruction import verify


class NariaiTransverseKantowskiSachsGlobalObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())

    def test_slabwise_and_global_states_are_distinct(self) -> None:
        self.assertEqual(self.value["theorem"]["slabwise_family"], "CERTIFIED")
        self.assertEqual(self.value["theorem"]["whole_cylinder_family"], "OBSTRUCTED")
        self.assertTrue(self.value["flags"]["TRANSVERSE_KS_SLABWISE_EINSTEIN_FAMILY"])
        self.assertFalse(self.value["flags"]["TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY"])

    def test_curvature_singularity_is_explicit(self) -> None:
        self.assertEqual(self.value["exact_obstruction"]["nariai_weyl_squared"], "16/3")
        self.assertIn("b**6", self.value["exact_obstruction"]["weyl_squared"])
        self.assertEqual(self.value["exact_obstruction"]["curvature_limit"], "+infinity as b->0+")

    def test_overclaims_are_rejected(self) -> None:
        for flag in (
            "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY",
            "ALL_TRANSVERSE_BACH_FLAT_FAMILIES_OBSTRUCTED",
            "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY",
            "NONLINEAR_BV_EXTENSION",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
