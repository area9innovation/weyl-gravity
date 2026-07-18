"""Focused tests for the row-ID compact-product chain-map export."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from bridge.einstein_sector.export_einstein_weyl_compact_product_chain_map_pbw import (
    OUTPUT,
    build_payload,
)
from bridge.einstein_sector.verify_einstein_weyl_compact_product_chain_map_pbw import (
    verify,
)


class EinsteinWeylProductChainMapPBWTest(unittest.TestCase):
    def test_export_is_current_and_verifies(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build_payload())
        verify()

    def test_row_id_corruption_is_rejected(self) -> None:
        payload = deepcopy(json.loads(OUTPUT.read_text()))
        payload["map"]["entries"][0]["input_row_id"] = "wrong_row"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload))
            with self.assertRaises((AssertionError, KeyError)):
                verify(path)

    def test_unproved_target_q1_replay_stays_false(self) -> None:
        payload = json.loads(OUTPUT.read_text())
        self.assertFalse(payload["checks"]["target_q1_composition_replayed"])
        self.assertNotIn("sigma_W", {
            entry["output_row_id"] for entry in payload["map"]["entries"]
        })
        self.assertNotIn("sigma_W_star", {
            entry["output_row_id"] for entry in payload["map"]["entries"]
        })


if __name__ == "__main__":
    unittest.main()
