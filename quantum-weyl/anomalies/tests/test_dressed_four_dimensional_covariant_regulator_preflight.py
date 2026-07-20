from __future__ import annotations

import copy
import unittest

from anomalies import dressed_four_dimensional_covariant_regulator_preflight as module


class DressedFourDimensionalRegulatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = module.build()

    def _rejects(self, mutator) -> None:
        changed = copy.deepcopy(self.value)
        mutator(changed)
        with self.assertRaises(ValueError):
            module.validate(changed)

    def test_baseline(self) -> None:
        module.validate(self.value)

    def test_measure_preserving_mutation_rejected(self) -> None:
        self._rejects(
            lambda value: value["regulated_canonical_map"].__setitem__(
                "raw_coefficient", 0
            )
        )

    def test_dropped_duhamel_term_rejected(self) -> None:
        self._rejects(
            lambda value: value["ward_symbol"].__setitem__(
                "Duhamel_term_zero_hypothesis", "ALWAYS_ZERO"
            )
        )

    def test_actual_breaking_promotion_rejected(self) -> None:
        self._rejects(
            lambda value: value["ward_symbol"].__setitem__(
                "actual_breaking", "COMPUTED"
            )
        )

    def test_scheme_identification_rejected(self) -> None:
        self._rejects(
            lambda value: value["scheme_comparison"].__setitem__(
                "equivalence_status", "IDENTICAL"
            )
        )

    def test_candidate_a_guess_rejected(self) -> None:
        self._rejects(
            lambda value: value["selected_action_receiver"][
                "candidate_A_scalar"
            ].__setitem__("status", "FILLED_WITH_GUESSED_K")
        )

    def test_candidate_b_guess_rejected(self) -> None:
        self._rejects(
            lambda value: value["selected_action_receiver"][
                "candidate_B_reducible_three_form"
            ].__setitem__("status", "FILLED_WITH_GUESSED_K")
        )

    def test_qap_promotion_rejected(self) -> None:
        self._rejects(
            lambda value: value["claim_flags"].__setitem__(
                "QAP_ESTABLISHED", True
            )
        )


if __name__ == "__main__":
    unittest.main()
