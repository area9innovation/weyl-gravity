from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from transfer.curvature_squared_covariant_log_gamma1 import build, validate
from transfer.verify_curvature_squared_covariant_log_gamma1 import verify


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class CurvatureSquaredCovariantLogGamma1Tests(unittest.TestCase):
    def test_certificate_builds_and_independently_replays(self) -> None:
        payload = build()
        validate(payload)
        verify()

    def test_exact_coefficient_scale_and_curvature_orders(self) -> None:
        payload = build()
        form = payload["covariant_curvature_squared_form_factor"]
        comparison = payload["operator_choice_independence"]
        self.assertEqual(_fraction(form["logarithmic_coefficient"]), Fraction(-199, 60))
        self.assertEqual(_fraction(form["RG_scale_response"]), Fraction(199, 30))
        self.assertEqual(form["curvature_order"], 2)
        self.assertEqual(comparison["first_difference_order"], 3)

    def test_complete_curved_remainder_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"]["COMPLETE_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED"] = True
        with self.assertRaises(Exception):
            validate(payload)

    def test_finite_normalization_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"]["FINITE_R2_NORMALIZATION_FIXED"] = True
        with self.assertRaises(Exception):
            validate(payload)

    def test_extended_contraction_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"]["EXTENDED_CLASSICAL_CONTRACTION_SUPPLIED"] = True
        with self.assertRaises(Exception):
            validate(payload)

    def test_residual_transfer_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["decision"]["residual_transfer"] = "AUTHORIZED"
        with self.assertRaises(Exception):
            validate(payload)


if __name__ == "__main__":
    unittest.main()
