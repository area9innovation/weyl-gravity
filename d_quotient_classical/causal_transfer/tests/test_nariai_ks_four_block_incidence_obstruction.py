from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.causal_transfer.nariai_ks_four_block_incidence_obstruction import build, validate
from d_quotient_classical.causal_transfer.verify_nariai_ks_four_block_incidence_obstruction import verify


class NariaiKSFourBlockIncidenceObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())

    def test_failure_starts_at_quadratic_order(self) -> None:
        exact = self.value["exact_symbol_obstruction"]
        self.assertEqual(exact["first_epsilon_derivative_at_zero"], "0")
        self.assertEqual(exact["second_epsilon_derivative_at_zero"], "-5/6")
        self.assertEqual(exact["minimal_fixed_presentation_incidence_count"], 6)
        self.assertTrue(exact["output_transport_invertible_on_range"])

    def test_formal_theorem_survives_but_finite_promotion_does_not(self) -> None:
        flags = self.value["flags"]
        self.assertTrue(flags["TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION"])
        self.assertFalse(flags["CANONICAL_KS_FOUR_BLOCK_FINITE_INCIDENCE"])
        self.assertFalse(flags["TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER"])

    def test_claim_guards(self) -> None:
        for flag in (
            "CANONICAL_KS_FOUR_BLOCK_FINITE_INCIDENCE",
            "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER",
            "ALL_SUPPORT_LOCAL_IDENTIFICATIONS_OBSTRUCTED",
            "ALL_BACH_FLAT_FAMILIES_OBSTRUCTED",
            "HADAMARD_STATE",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
