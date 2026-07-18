import json
import unittest

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_full_bv_coderivation_redefinition as result,
)


class ZeroJetFullBVRedefinitionTests(unittest.TestCase):
    def test_normalized_witness_replays(self) -> None:
        replay = result.witness_replay()
        self.assertEqual(replay["normalized_target_evaluation"], "1")
        self.assertEqual(replay["annihilated_F2_columns"], 810)
        self.assertEqual(replay["annihilated_F3_columns"], 4160)

    def test_typed_half_weight_is_not_truncated(self) -> None:
        lift = result.cotangent_column(3, (27, 27))
        self.assertEqual(str(lift[(31, (13, 27))]), "-1/2")

    def test_positive_pbw_words_have_no_scalar_reduction(self) -> None:
        replay = result.pbw_augmentation_replay()
        self.assertEqual(replay["scalar_output_defects"], 0)
        self.assertEqual(replay["positive_input_words_checked"], 5460)

    def test_claim_remains_fail_closed(self) -> None:
        value = json.loads(result.OUTPUT.read_text())
        self.assertFalse(value["claim_flags"]["FULL_JET_BOUNDED_CYCLIC_DEFORMATION_CLASS_DECIDED"])
        self.assertFalse(value["claim_flags"]["QUANTUM_CLAIM"])


if __name__ == "__main__":
    unittest.main()
