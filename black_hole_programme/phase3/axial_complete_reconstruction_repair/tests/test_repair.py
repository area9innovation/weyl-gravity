from __future__ import annotations

import json
import unittest
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_complete_reconstruction_repair import produce


HERE = Path(__file__).resolve().parents[1]


class CompleteRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = json.loads((HERE / "certificate.json").read_text())

    def test_dimension_split(self):
        dims = self.cert["dimension_and_rank"]
        self.assertEqual((dims["carrier_dimension"],
                          dims["Einstein_kernel_dimension"],
                          dims["complete_metric_dimension"]), (4, 2, 6))

    def test_both_endpoint_bases_have_six_columns(self):
        for side in ("horizon", "infinity"):
            self.assertEqual(len(self.cert["endpoint_bases"][side]["columns"]), 6)
            self.assertEqual(self.cert["endpoint_bases"][side]["rank"], 6)

    def test_horizon_resonances_are_compatible(self):
        lifts = self.cert["endpoint_bases"]["horizon"]["additional_lifts"]
        self.assertEqual(lifts["XH0a"]["resonances"][0]["obstruction"], "0")
        self.assertEqual(lifts["XH0b"]["resonances"][0]["obstruction"], "0")
        self.assertEqual(lifts["XHminus"]["resonances"][0]["order"], 1)

    def test_x0_repair_and_legacy_e0(self):
        x = self.cert["x0_and_legacy_reaudit"]
        self.assertEqual(x["repair"]["C_after_repair"], "0")
        self.assertIn("NOT_AN_EINSTEIN", x["legacy_E0"]["disposition"])

    def test_pilot_has_no_exception(self):
        self.assertEqual(self.cert["exceptional_set"]["real_pilot_interval"], [])


if __name__ == "__main__":
    unittest.main()
