from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from spectral.euclidean.generic_background_physical_hessian_mixed_h1_h2_corner_fixture import build, validate
from spectral.euclidean.verify_generic_background_physical_hessian_mixed_h1_h2_corner_fixture import verify


class GenericBackgroundPhysicalHessianMixedH1H2CornerFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_all_labelled_trace_log_rows_are_present(self) -> None:
        h1 = self.value["three_H1_corner"]
        h2 = self.value["mixed_H1_H2_endpoint"]
        self.assertEqual(h1["cyclic_multiplicity_per_orientation"], 3)
        self.assertEqual(h2["bubble_count"], 3)
        self.assertEqual(h2["endpoint_count"], 6)

    def test_operational_h2_is_rank_nine_and_self_adjoint(self) -> None:
        for row in self.value["operational_H2"]["bubble_rows"]:
            self.assertEqual(row["H2_covariant_rank"], 9)
            self.assertEqual(row["H2_representation_rank"], 9)

    def test_raw_combined_logarithm_is_nonzero(self) -> None:
        combined = self.value["combined_raw_logarithm"]
        value = Fraction(combined["sum"]["numerator"], combined["sum"]["denominator"])
        self.assertEqual(value, Fraction(15707, 216))
        self.assertNotEqual(value, 0)

    def test_subtraction_and_m14_disposition_stay_open(self) -> None:
        flags = self.value["claim_flags"]
        self.assertFalse(flags["RENORMALIZED_SUBTRACTION_FIXED"])
        self.assertFalse(flags["PHYSICAL_M14_CORNER_CLASS_DISPOSED"])
        self.assertFalse(flags["QME_OR_ANOMALY_STATUS_CHANGED"])

    def test_overpromotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["RENORMALIZED_SUBTRACTION_FIXED"] = True
        with self.assertRaises(Exception):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(self.value), self.value)


if __name__ == "__main__":
    unittest.main()
