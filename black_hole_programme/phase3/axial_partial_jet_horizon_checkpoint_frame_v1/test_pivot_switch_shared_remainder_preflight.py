from __future__ import annotations

import json
import unittest
from pathlib import Path

from . import pivot_switch_shared_remainder_preflight as preflight

HERE = Path(__file__).resolve().parent


class SharedRemainderPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(
            (HERE / "pivot-switch-shared-remainder-preflight-run.json").read_text()
        )

    def test_uses_corrected_source(self) -> None:
        self.assertEqual(self.data["source"]["last_valid_panel"], 30)
        self.assertEqual(self.data["source"]["rho"], "95/268435456")

    def test_one_next_step(self) -> None:
        self.assertEqual(self.data["target"]["panel"], 31)
        self.assertEqual(self.data["target"]["rho"], "3/8388608")
        self.assertTrue(self.data["raw_step"]["state_finite"])

    def test_shared_reciprocal_is_post_normalization_finite(self) -> None:
        representation = self.data["representation"]
        self.assertTrue(representation["normalization"]["passed"])
        self.assertTrue(representation["post_normalization_finite"])
        self.assertEqual(
            self.data["checkpoint"]["line"]["base"][2]["ball"],
            "1.000000000000000000000000000000000000000000000000000000000000000000000000000",
        )
        self.assertEqual(self.data["checkpoint"]["line"]["tangent"][2]["ball"], "0")

    def test_mutant_eager_squared_denominator_is_killed(self) -> None:
        mutant = self.data["representation"]["eager_squared_denominator_mutant"]
        self.assertTrue(mutant["denominator_contains_zero"])
        self.assertFalse(mutant["normalized_tangent_finite"])
        self.assertFalse(mutant["mutant_accepts"])

    def test_recompute(self) -> None:
        self.assertEqual(preflight.compute(), self.data)


if __name__ == "__main__":
    unittest.main()
