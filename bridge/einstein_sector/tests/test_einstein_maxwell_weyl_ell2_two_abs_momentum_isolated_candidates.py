from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class TwoAbsMomentumCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json").read_text())

    def test_candidate_ledger_has_21_distinct_rows(self) -> None:
        ledger = self.value["candidate_ledger"]
        self.assertEqual(ledger["positive_admissible_rows"], 21)
        self.assertEqual(ledger["distinct_positive_rho_values"], 21)

    def test_all_signs_are_exact(self) -> None:
        self.assertFalse(self.value["exact_sign_method"]["floating_point_decisions"])
        self.assertTrue(all(row["rho_positive_exact"] for row in self.value["candidate_ledger"]["rows"]))

    def test_sum_and_difference_channels_survive(self) -> None:
        channels = {row["admissible_temporal_channel"] for row in self.value["candidate_ledger"]["rows"]}
        self.assertEqual(channels, {"SUM", "DIFFERENCE"})

    def test_sources_and_cone_remain_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["projected_source_coefficients_computed"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
