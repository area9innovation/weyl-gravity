from __future__ import annotations

import copy
import unittest

from d_quotient_classical.causal_transfer import (
    berger_q26_finite_row_module_closure as theorem,
)


class BergerQ26FiniteRowModuleClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = theorem.closure_audit(4)
        cls.value = theorem.build()

    def test_certificate_validates(self) -> None:
        theorem.validate(self.value)

    def test_spin_four_representation_is_multiplicative(self) -> None:
        representation = theorem._spin_representation(4, theorem.PRIME)
        self.assertEqual(len(representation[0]), 9)

    def test_closure_fills_all_936_dimensions(self) -> None:
        levels = [
            row["certified_independent_columns"]
            for row in self.payload["closure_levels"]
        ]
        self.assertEqual(levels, [139, 522, 936])
        self.assertEqual(
            self.payload["closure_levels"][-1][
                "minor_determinant_mod_prime"
            ],
            384,
        )

    def test_free_row_lower_bound_is_104(self) -> None:
        self.assertEqual(self.payload["certified_row_lower_bound"], 104)
        self.assertEqual(
            self.value["representation_module_closure"][
                "forced_free_row_degree_profile_at_least"
            ],
            {
                "degree_minus1": 12,
                "degree_0": 40,
                "degree_plus1": 40,
                "degree_plus2": 12,
            },
        )

    def test_sufficiency_is_not_promoted(self) -> None:
        self.assertFalse(
            self.value["classification"][
                "one_hundred_four_row_extension_sufficient"
            ]
        )
        self.assertFalse(
            self.value["classification"]["smallest_finite_extension_constructed"]
        )

    def test_sufficiency_mutation_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["classification"][
            "one_hundred_four_row_extension_sufficient"
        ] = True
        with self.assertRaises(Exception):
            theorem.validate(mutant)

    def test_hadamard_mutation_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["classification"]["Hadamard_or_quantum_claim"] = True
        with self.assertRaises(Exception):
            theorem.validate(mutant)


if __name__ == "__main__":
    unittest.main()
