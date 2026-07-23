from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ..compose_child_global import verify_global
from ..verify_handoff import HandoffError


HERE = Path(__file__).resolve()
ARTIFACTS = HERE.parents[1] / "artifacts"
PREFIX = ARTIFACTS / "prefix_join_0_to_191over8.json"
TAIL = ARTIFACTS / "child_tail_joins" / "child_tail_join_q00.json"
GLOBAL = ARTIFACTS / "global_maps" / "global_map_q00.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


class ChildGlobalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prefix = _load(PREFIX)
        cls.tail = _load(TAIL)
        cls.global_map = _load(GLOBAL)

    def test_q0_global_map_replays_without_scratch_files(self) -> None:
        self.assertTrue(
            verify_global(self.global_map, self.prefix, self.tail, 0)
        )

    def test_false_restart_is_rejected(self) -> None:
        payload = copy.deepcopy(self.global_map)
        payload["composition"]["physical_restart"] = True
        with self.assertRaisesRegex(HandoffError, "false restart"):
            verify_global(payload, self.prefix, self.tail, 0)

    def test_permutation_drift_is_rejected(self) -> None:
        payload = copy.deepcopy(self.global_map)
        payload["block_to_standard_permutation"][
            "standard_to_block_index"
        ][4:6] = reversed(
            payload["block_to_standard_permutation"][
                "standard_to_block_index"
            ][4:6]
        )
        with self.assertRaisesRegex(HandoffError, "exact crosswalk drift"):
            verify_global(payload, self.prefix, self.tail, 0)

    def test_unpermuted_standard_map_is_rejected(self) -> None:
        payload = copy.deepcopy(self.global_map)
        payload["standard_realified_map"] = copy.deepcopy(
            payload["block_order_map"]
        )
        with self.assertRaisesRegex(HandoffError, "permutation not applied"):
            verify_global(payload, self.prefix, self.tail, 0)

    def test_projection_before_permutation_is_rejected(self) -> None:
        payload = copy.deepcopy(self.global_map)
        payload["projection_contract"][
            "permutation_applied_before_projection"
        ] = False
        with self.assertRaisesRegex(HandoffError, "projection ordering"):
            verify_global(payload, self.prefix, self.tail, 0)

    def test_prefix_payload_drift_is_rejected(self) -> None:
        payload = copy.deepcopy(self.global_map)
        payload["integrity"]["prefix"]["payload_sha256"] = "0" * 64
        with self.assertRaisesRegex(HandoffError, "prefix/tail payload drift"):
            verify_global(payload, self.prefix, self.tail, 0)


if __name__ == "__main__":
    unittest.main()
