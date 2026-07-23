from __future__ import annotations

import copy
import unittest

from ..state_permutation import (
    STANDARD_TO_BLOCK_INDEX,
    permutation_payload,
    verify_permutation,
)
from ..verify_handoff import HandoffError


class StatePermutationTest(unittest.TestCase):
    def test_exact_permutation_is_frozen(self) -> None:
        self.assertEqual(
            STANDARD_TO_BLOCK_INDEX,
            (0, 1, 2, 3, 8, 9, 4, 5, 6, 7, 10, 11),
        )
        self.assertTrue(verify_permutation(permutation_payload()))

    def test_swapped_block_standard_crosswalk_is_rejected(self) -> None:
        payload = copy.deepcopy(permutation_payload())
        payload["standard_to_block_index"][4:6] = reversed(
            payload["standard_to_block_index"][4:6]
        )
        with self.assertRaisesRegex(HandoffError, "exact crosswalk drift"):
            verify_permutation(payload)

    def test_false_physical_restart_is_rejected(self) -> None:
        payload = copy.deepcopy(permutation_payload())
        payload["physical_restart"] = True
        with self.assertRaisesRegex(HandoffError, "exact crosswalk drift"):
            verify_permutation(payload)


if __name__ == "__main__":
    unittest.main()
