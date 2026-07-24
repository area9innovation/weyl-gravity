from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from . import shared_remainder_multipanel_successor as successor

HERE = Path(__file__).resolve().parent


class SharedRemainderMultipanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(
            (HERE / "shared-remainder-multipanel-successor-run.json").read_text()
        )

    def test_nine_substeps_are_accepted(self) -> None:
        self.assertEqual(self.data["accepted_substeps"], 9)
        self.assertEqual(len(self.data["checkpoint_chain"]), 9)
        self.assertEqual(len(self.data["gate_ledger"]), 9)

    def test_chain_is_content_addressed(self) -> None:
        parent = self.data["source"]["sha256"]
        for checkpoint in self.data["checkpoint_chain"]:
            self.assertEqual(checkpoint["parent_sha256"], parent)
            payload = {
                key: value
                for key, value in checkpoint.items()
                if key != "content_sha256"
            }
            self.assertEqual(
                successor.canonical_hash(payload),
                checkpoint["content_sha256"],
            )
            parent = checkpoint["content_sha256"]

    def test_content_mutation_is_detected(self) -> None:
        checkpoint = copy.deepcopy(self.data["checkpoint_chain"][0])
        original = checkpoint.pop("content_sha256")
        checkpoint["rho"] = "0"
        self.assertNotEqual(successor.canonical_hash(checkpoint), original)

    def test_terminal_pivot_obstruction_is_fail_closed(self) -> None:
        terminal = self.data["terminal"]
        self.assertEqual(terminal["gate"], "FIXED_ATLAS_PIVOT_OBSTRUCTION")
        self.assertIsNone(terminal["selected"])
        self.assertTrue(
            all(value == "0" for value in terminal["atlas_modulus_lowers"].values())
        )
        self.assertFalse(self.data["claim_flags"]["next_base_panel_completed"])

    def test_recompute(self) -> None:
        self.assertEqual(successor.compute(), self.data)


if __name__ == "__main__":
    unittest.main()
