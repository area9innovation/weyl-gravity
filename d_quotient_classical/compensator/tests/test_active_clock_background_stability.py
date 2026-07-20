from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_active_clock_background_stability import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1.json"
)


class ActiveClockBackgroundStabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_exact_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_stationary_coefficient_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        entry = mutated["stationary_evaluation"]["stacked_matrix"]["entries"][0]
        entry["coefficient"] = "37*kappa**2"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_kernel_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["stationary_locus_and_rank_strata"]["kernel_generator_K"][0] = (
            "8*nu**4*(12*kappa+q-3)"
        )
        with self.assertRaises(Exception):
            verify(mutated)

    def test_box_cannot_cross_bifurcation(self) -> None:
        mutated = deepcopy(self.value)
        mutated["certified_open_neighbourhood"]["exact_box"]["q"][1] = "3/10"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_longitudinal_witness_cannot_be_dropped(self) -> None:
        mutated = deepcopy(self.value)
        mutated["first_bifurcation"]["above_witness"][
            "p1_PX_longitudinal"
        ][2] = "1"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_rank_and_principal_bifurcations_remain_distinct(self) -> None:
        mutated = deepcopy(self.value)
        mutated["first_bifurcation"]["surface_data"]["stationary_rank"] = 4
        with self.assertRaises(Exception):
            verify(mutated)

    def test_fixed_action_promotion_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["ONE_FIXED_ACTION_BACKGROUND_STABILITY"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_generic_and_quantum_promotions_rejected(self) -> None:
        for key in (
            "GENERIC_BACKGROUND_NO_GO",
            "HADAMARD_ANOMALY_QME_OR_QUANTUM",
        ):
            with self.subTest(key=key):
                mutated = deepcopy(self.value)
                mutated["claim_flags"][key] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
