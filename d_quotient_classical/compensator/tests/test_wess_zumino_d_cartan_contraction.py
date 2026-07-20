from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.compensator.wess_zumino_d_cartan_contraction import (
    build,
    validate,
)
from d_quotient_classical.compensator.verify_wess_zumino_d_cartan_contraction import (
    verify,
)


class WessZuminoDCartanContractionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_producer_and_independent_verifier_agree(self) -> None:
        validate(self.value)
        verify(self.value)

    def test_raw_generator_is_not_berger_generator(self) -> None:
        generator = self.value["generator"]
        self.assertEqual(generator["generator_id"], "D_compact")
        self.assertFalse(generator["is_K_Berger"])
        self.assertFalse(
            self.value["formal_field_algebra"]["WZ_tau_is_Berger_clock"]
        )

    def test_cartan_weights_include_nonzero_mutation_fixtures(self) -> None:
        self.assertEqual(
            [
                row["D_weight"]
                for row in self.value["matrix_fixtures"][
                    "cartan_weight_fixtures"
                ]
            ],
            [-2, 0, 3],
        )

    def test_minkowski_affine_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        row = mutant["affine_Weyl_component_gate"]["rows"][
            "minkowski_D_M_cross_check"
        ]
        row["contraction_equivariant"] = True
        with self.assertRaises((AssertionError, ValueError)):
            verify(mutant)

    def test_quantum_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["QUANTUM_D_CARTAN_DEFECT_CLASSIFIED"] = True
        with self.assertRaises((AssertionError, ValueError)):
            verify(mutant)

    def test_pairing_sign_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        entries = mutant["matrix_fixtures"]["quartet_pairing"]["entries"]
        ghost_entry = next(
            entry
            for entry in entries
            if entry["row"] == 1 and entry["column"] == 2
        )
        ghost_entry["coefficient"] = 1
        with self.assertRaises(AssertionError):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
