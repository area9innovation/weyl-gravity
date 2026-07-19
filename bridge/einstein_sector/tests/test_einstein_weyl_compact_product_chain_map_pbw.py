"""Focused tests for the row-ID compact-product chain-map export."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
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

    def test_target_q1_replay_is_exact_and_weyl_rows_have_zero_image(self) -> None:
        payload = json.loads(OUTPUT.read_text())
        self.assertTrue(payload["checks"]["target_q1_composition_replayed"])
        result = verify()
        self.assertEqual(result["defect_counts"], [0] * 40)
        self.assertNotIn("sigma_W", {
            entry["output_row_id"] for entry in payload["map"]["entries"]
        })
        self.assertNotIn("sigma_W_star", {
            entry["output_row_id"] for entry in payload["map"]["entries"]
        })

    def test_maxwell_cotangent_sign_regression_is_rejected(self) -> None:
        payload = deepcopy(json.loads(OUTPUT.read_text()))
        entry = next(
            item
            for item in payload["map"]["entries"]
            if item["output_row_id"].startswith("g_")
            and item["output_row_id"].endswith("_star")
            and item["input_row_id"].startswith("A_")
            and item["input_row_id"].endswith("_star")
        )
        for term in entry["terms"]:
            for jet in term["coefficient_jets"]:
                jet["coefficient"] = str(-Fraction(jet["coefficient"]))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong-sign.json"
            path.write_text(json.dumps(payload))
            with self.assertRaises(AssertionError):
                verify(path)


if __name__ == "__main__":
    unittest.main()
