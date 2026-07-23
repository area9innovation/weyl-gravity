from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ..infinity_plane_contract import contract_payload, verify_contract
from ..verify_handoff import HandoffError


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "artifacts"
    / "infinity_physical_plane_contract.json"
)


class InfinityPlaneContractTest(unittest.TestCase):
    def test_generated_contract_replays(self) -> None:
        self.assertTrue(verify_contract(contract_payload()))

    def test_committed_contract_replays(self) -> None:
        self.assertTrue(verify_contract(json.loads(ARTIFACT.read_text())))

    def test_noncomplementary_selector_is_rejected(self) -> None:
        payload = copy.deepcopy(contract_payload())
        payload["selectors"]["Iplus"][0] = 0
        with self.assertRaisesRegex(HandoffError, "exact payload drift"):
            verify_contract(payload)

    def test_false_combined_rank_is_rejected(self) -> None:
        payload = copy.deepcopy(contract_payload())
        payload["combined_standard_basis"]["rank"] = 11
        with self.assertRaisesRegex(HandoffError, "exact payload drift"):
            verify_contract(payload)

    def test_state_permutation_drift_is_rejected(self) -> None:
        payload = copy.deepcopy(contract_payload())
        payload["trace_coordinate_selectors"][
            "Iminus_block_12_by_6"
        ][0][0] = "0/1"
        with self.assertRaisesRegex(HandoffError, "exact payload drift"):
            verify_contract(payload)


if __name__ == "__main__":
    unittest.main()
