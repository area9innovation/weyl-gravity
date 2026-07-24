from __future__ import annotations

import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class CheckpointResumeTest(unittest.TestCase):
    def test_checkpoint_carries_full_mixed_model(self) -> None:
        checkpoint = json.loads((HERE / "checkpoint.json").read_text())
        payload = checkpoint["payload"]
        for name in ("base", "tangent"):
            model = payload[name]
            self.assertEqual(model["schema"], "ivtaylor-degree4-v1")
            self.assertEqual(len(model["coefficients"]), 5)
            self.assertEqual(len(model["remainder_bits"]), 4)

    def test_restart_is_replay_free(self) -> None:
        source = (HERE / "restart_chunk.forge").read_text()
        self.assertNotIn("build_seed(", source)
        self.assertIn("checkpoint_base()", source)
        self.assertIn("checkpoint_tangent()", source)
        self.assertIn('big("2015/64")', source)

    def test_flags_fail_closed(self) -> None:
        document = json.loads((HERE / "certificate.json").read_text())
        self.assertFalse(document["claim_flags"]["Rplus_reaches_r4"])
        self.assertFalse(document["claim_flags"]["T_plus_recovered"])
        self.assertFalse(
            document["claim_flags"]["complementary_outgoing_columns_constructed"]
        )


if __name__ == "__main__":
    unittest.main()
