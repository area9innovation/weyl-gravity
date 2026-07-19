"""Tests for exceptional L2 difference-frequency nonresonance."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance import OUTPUT, build


class DifferenceFrequencyNonresonanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_all_generic_pairs(self) -> None:
        records = self.value["generic_generic_elimination"]["records"]
        self.assertEqual(len(records), 27)
        self.assertTrue(all(not row["integer_roots_at_least_2"] for row in records))

    def test_all_dipole_pairs(self) -> None:
        records = self.value["dipole_generic_elimination"]["records"]
        self.assertEqual(len(records), 12)
        self.assertTrue(all(row["minimal_polynomial_constant"] != "0" for row in records))

    def test_complete_k0_frequency_census(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["no_k0_difference_frequency_collision"])
        self.assertTrue(classification["complete_k0_frequency_census_closed"])

    def test_fail_closed_source_and_momentum(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["positive_sum_live_global_times_ell2_extra_source_classified"])
        self.assertFalse(classification["opposite_nonzero_momenta_classified"])
        self.assertFalse(classification["bounded_mixed_cone_classified"])


if __name__ == "__main__":
    unittest.main()
