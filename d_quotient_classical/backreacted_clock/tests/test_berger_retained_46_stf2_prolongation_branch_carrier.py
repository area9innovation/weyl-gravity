import copy
import unittest

from d_quotient_classical.backreacted_clock.berger_retained_46_stf2_prolongation_branch_carrier import (
    build,
    verify,
)


class Retained46STF2CarrierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, _ = build()

    def test_exact_carrier(self):
        verify(self.payload)
        self.assertEqual(self.payload["carrier"]["degree_ranks"], {"-1": 4, "0": 19, "1": 19, "2": 4})
        self.assertTrue(all(self.payload["exact_checks"].values()))
        self.assertTrue(self.payload["exact_checks"]["graph_shear_inverse"])
        self.assertTrue(self.payload["exact_checks"]["graph_shear_typed_cyclic"])
        self.assertEqual(self.payload["artifacts"]["graph_shear_U_46"]["shape"], [46, 46])

    def test_projector_promotion_is_rejected(self):
        mutant = copy.deepcopy(self.payload)
        mutant["flags"]["CANONICAL_BRANCH_PROJECTOR_CERTIFIED"] = True
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_branch_mixing_promotion_is_rejected(self):
        mutant = copy.deepcopy(self.payload)
        mutant["flags"]["ELL3_BRANCH_MIXING_AUTHORIZED"] = True
        with self.assertRaises(AssertionError):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
