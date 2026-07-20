from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_minimal_action_classification_after_neither import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1.json"
)


class MinimalActionClassificationAfterNeitherTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independent_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_comparison_hash_drift_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["dependencies"]["candidate_AB_comparison"]["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            verify(mutated)

    def test_cylinder_equation_mutation_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        matrix = mutated["stationary_background_equations"]["unit_cylinder"][
            "matrix"
        ]
        next(
            item
            for item in matrix["entries"]
            if item["row"] == 0 and item["column"] == 1
        )["coefficient"] = "35"
        with self.assertRaises(AssertionError):
            verify(mutated)

    def test_berger_equation_mutation_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        matrix = mutated["stationary_background_equations"][
            "frozen_Berger_clock"
        ]["matrix"]
        next(
            item
            for item in matrix["entries"]
            if item["row"] == 2 and item["column"] == 0
        )["coefficient"] = "0"
        with self.assertRaises(AssertionError):
            verify(mutated)

    def test_separator_rank_cannot_be_lowered(self) -> None:
        mutated = deepcopy(self.value)
        mutated["stationary_background_equations"]["no_HT_stacked_system"][
            "rank"
        ] = 4
        with self.assertRaises(Exception):
            verify(mutated)

    def test_scalar_split_inertia_cannot_be_hidden(self) -> None:
        mutated = deepcopy(self.value)
        mutated["quadratic_and_global_analysis"]["scalar_auxiliary"][
            "velocity_inertia"
        ] = [2, 0, 0]
        with self.assertRaises(Exception):
            verify(mutated)

    def test_ht_global_kernel_cannot_be_deleted(self) -> None:
        mutated = deepcopy(self.value)
        mutated["quadratic_and_global_analysis"]["HT_topological"][
            "zero_frequency_kernel"
        ] = ["0", "0", "0"]
        with self.assertRaises(Exception):
            verify(mutated)

    def test_compact_support_class_cannot_be_deleted(self) -> None:
        mutated = deepcopy(self.value)
        mutated["topology"]["compact_support_betti_Hc0_to_Hc4"] = [
            0,
            1,
            0,
            0,
            0,
        ]
        with self.assertRaises(Exception):
            verify(mutated)

    def test_empty_locus_cannot_export_candidate_c(self) -> None:
        mutated = deepcopy(self.value)
        mutated["selection"]["candidate_C_selected"] = True
        mutated["selection"]["candidate_C_action"] = "invented action"
        mutated["selection"]["candidate_C_action_hash"] = "1" * 64
        with self.assertRaises(Exception):
            verify(mutated)

    def test_hybrid_cannot_be_selected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["selection"]["hybrid_selected"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_scoped_class_cannot_be_broadened_or_quantized(self) -> None:
        for flag in ("UNIVERSAL_COMPENSATOR_NO_GO", "HADAMARD_OR_QUANTUM_RESULT"):
            with self.subTest(flag=flag):
                mutated = deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
