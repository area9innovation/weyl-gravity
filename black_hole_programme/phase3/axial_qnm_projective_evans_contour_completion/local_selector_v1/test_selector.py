#!/usr/bin/env python3
"""Fast mutation checks for the local selector certificate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class LocalSelectorCertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads((HERE / "certificate.json").read_text())

    def test_reduced_spin_two_selector_is_promoted(self) -> None:
        flags = self.document["claim_flags"]
        self.assertTrue(flags["unique_simple_spin_two_qnm_localized"])
        self.assertTrue(flags["intrinsic_tangent_selector_nonzero"])
        self.assertTrue(flags["repeated_spin_two_smith_valuations_0_2"])

    def test_full_connection_and_resolvent_remain_fail_closed(self) -> None:
        flags = self.document["claim_flags"]
        self.assertFalse(flags["full_connection_smith_valuations_0_0_2"])
        self.assertFalse(flags["physical_fredholm_realization_constructed"])
        self.assertFalse(
            flags["green_resolvent_second_order_pole_established"]
        )

    def test_local_zero_is_simple(self) -> None:
        qnm = self.document["result"]["qnm_enclosure"]
        self.assertEqual(qnm["zero_count_with_multiplicity"], 1)
        self.assertTrue(qnm["simple"])


if __name__ == "__main__":
    unittest.main()
