from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from transfer.flat_tt_logarithmic_gamma1 import build, validate
from transfer.verify_flat_tt_logarithmic_gamma1 import verify


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class FlatTTLogarithmicGamma1Tests(unittest.TestCase):
    def test_certificate_builds_and_independently_replays(self) -> None:
        payload = build()
        validate(payload)
        verify()

    def test_exact_log_coefficient_and_scale_response(self) -> None:
        payload = build()["exact_logarithmic_form_factor"]
        self.assertEqual(_fraction(payload["logarithmic_coefficient"]), Fraction(-199, 60))
        self.assertEqual(_fraction(payload["RG_scale_response"]), Fraction(199, 30))
        self.assertEqual(_fraction(payload["heat_kernel_beta2"]), Fraction(199, 15))

    def test_finite_constant_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"]["FINITE_C2_NORMALIZATION_FIXED"] = True
        with self.assertRaises(Exception):
            validate(payload)

    def test_curved_completion_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"]["GENERAL_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED"] = True
        with self.assertRaises(Exception):
            validate(payload)

    def test_zero_mode_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["excluded_promotions"]["zero_momentum"] = "INCLUDED"
        with self.assertRaises(Exception):
            validate(payload)

    def test_residual_transfer_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["decision"]["residual_transfer"] = "AUTHORIZED"
        with self.assertRaises(Exception):
            validate(payload)


if __name__ == "__main__":
    unittest.main()
