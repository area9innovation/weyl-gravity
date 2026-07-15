from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.berger_minimal_bv_clock_sdr import (
    BergerMinimalBVClockSDR,
)


class BergerMinimalBVClockSDRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = BergerMinimalBVClockSDR.build().payload

    def test_clock_gauge_columns_split(self) -> None:
        incidence = self.payload["gauge_incidence"]
        self.assertTrue(incidence["temporal_and_weyl_columns_removed_from_metric"])
        self.assertEqual(incidence["clock_incidence_determinant"], -1)

    def test_all_minimal_clock_duals_are_included(self) -> None:
        block = self.payload["clock_block"]
        self.assertEqual(len(block["ordered_rows"]), 8)
        self.assertTrue(block["minimal_clock_rows_complete"])
        self.assertIn("q1 s+s q1=1_clock", block["identities"])

    def test_canonical_support_local_sdr(self) -> None:
        self.assertTrue(
            self.payload["canonical_antifield_lift"]["canonical_pairing_preserved"]
        )
        self.assertTrue(self.payload["field_coordinates"]["support_local"])
        self.assertEqual(self.payload["sdr"]["retained_minimal_dimension"], 26)

    def test_open_work_is_not_promoted(self) -> None:
        flags = self.payload["flags"]
        self.assertFalse(flags["retained_dressed_metric_q1_coefficients_complete"])
        self.assertFalse(flags["gauge_fixed_nonminimal_rows_complete"])
        self.assertFalse(flags["retained_operator_stability_proved"])
        self.assertFalse(flags["causal_green_homotopy_constructed"])
        self.assertFalse(flags["full_Berger_clock_BV_theorem"])


if __name__ == "__main__":
    unittest.main()
