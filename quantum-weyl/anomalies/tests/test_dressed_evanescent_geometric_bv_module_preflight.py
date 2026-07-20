from __future__ import annotations

import copy
import unittest

from anomalies import dressed_evanescent_geometric_bv_module_preflight as module


class DressedEvanescentGeometricBVTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = module.build()

    def _rejects(self, mutator) -> None:
        changed = copy.deepcopy(self.value)
        mutator(changed)
        with self.assertRaises(ValueError):
            module.validate(changed)

    def test_baseline(self) -> None:
        module.validate(self.value)
        self.assertEqual(
            self.value["full_bv_obstruction"]["first_missing_object"],
            "ACTION_SELECTED_D_DIMENSIONAL_KOSZUL_TATE_DIFFERENTIAL",
        )

    def test_identifying_euler_before_subtraction_rejected(self) -> None:
        self._rejects(
            lambda value: value["evanescent_continuations"][
                "minimal_subtraction_projection_commutator_witness"
            ].__setitem__("difference_nonzero", False)
        )

    def test_full_module_promotion_rejected(self) -> None:
        self._rejects(
            lambda value: value["claim_flags"].__setitem__(
                "FULL_EVANESCENT_BV_MODULE_COMPLETE", True
            )
        )

    def test_action_independent_mixing_promotion_rejected(self) -> None:
        self._rejects(
            lambda value: value["full_bv_obstruction"].__setitem__(
                "one_loop_mixing_map", "COMPUTED"
            )
        )

    def test_candidate_a_guess_rejected(self) -> None:
        self._rejects(
            lambda value: value["selected_action_extension_receiver"][
                "candidate_A_scalar"
            ].__setitem__("status", "FILLED_WITH_GUESSED_ROWS")
        )

    def test_candidate_b_guess_rejected(self) -> None:
        self._rejects(
            lambda value: value["selected_action_extension_receiver"][
                "candidate_B_reducible_three_form"
            ].__setitem__("status", "FILLED_WITH_GUESSED_ROWS")
        )

    def test_projection_mutation_rejected_by_proof_hash(self) -> None:
        self._rejects(
            lambda value: value["four_dimensional_projection"].__setitem__(
                "projection_rank", 3
            )
        )


if __name__ == "__main__":
    unittest.main()
