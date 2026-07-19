from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.causal_transfer.nariai_rank310_finite_hpl_incidence import build, validate
from d_quotient_classical.causal_transfer.verify_nariai_rank310_finite_hpl_incidence import verify


class NariaiRank310FiniteHPLIncidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())

    def test_series_terminates_support_locally(self) -> None:
        self.assertEqual(self.value["exact_fixture"]["inverse_series_length"], 2)
        self.assertFalse(self.value["analytic_consequence"]["nonlocal_HPL_inverse_required"])
        self.assertFalse(self.value["analytic_consequence"]["support_enlargement_from_SDR"])

    def test_every_polynomial_identity_is_exact(self) -> None:
        self.assertTrue(all(count == 0 for count in self.value["exact_fixture"]["nilpotence_defect_counts"].values()))
        self.assertTrue(all(count == 0 for count in self.value["exact_fixture"]["identity_defect_counts"].values()))
        self.assertEqual(self.value["exact_fixture"]["metric_higher_order_defects"], 0)

    def test_geometric_promotion_remains_guarded(self) -> None:
        for flag in (
            "TRANSVERSE_EXACT_GEOMETRIC_RANK310_FAMILY",
            "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY",
            "ALL_BACH_FLAT_BACKGROUNDS",
            "HADAMARD_STATE",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
