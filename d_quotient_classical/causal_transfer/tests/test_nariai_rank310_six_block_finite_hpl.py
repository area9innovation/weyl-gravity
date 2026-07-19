from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.causal_transfer.nariai_rank310_six_block_finite_hpl import build, validate
from d_quotient_classical.causal_transfer.verify_nariai_rank310_six_block_finite_hpl import verify


class NariaiRank310SixBlockFiniteHPLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())

    def test_resolvents_terminate(self) -> None:
        fixture = self.value["exact_fixture"]
        self.assertEqual(fixture["inverse_series_length"], 2)
        self.assertTrue(all(count == 0 for count in fixture["identity_defect_counts"].values()))

    def test_metric_cross_terms_are_retained(self) -> None:
        corrections = self.value["exact_fixture"]["metric_quadratic_cross_corrections"]
        self.assertEqual(len(corrections), 2)
        self.assertFalse(self.value["analytic_consequence"]["quadratic_metric_cross_terms_may_be_dropped"])

    def test_geometric_and_causal_gates_remain_false(self) -> None:
        for flag in (
            "KS_SIX_BLOCK_GEOMETRIC_COEFFICIENT_BINDING",
            "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER",
            "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY",
            "HADAMARD_STATE",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
