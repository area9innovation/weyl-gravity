from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from transfer.fv_conformized_c2_log_gamma1 import build, validate
from transfer.verify_fv_conformized_c2_log_gamma1 import verify


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class FVConformizedC2LogGamma1Tests(unittest.TestCase):
    def test_certificate_builds_and_independently_replays(self) -> None:
        payload = build()
        validate(payload)
        verify()

    def test_exact_coefficient_weight_and_curvature_filtration(self) -> None:
        payload = build()
        self.assertEqual(
            _fraction(payload["fv_scalar_flat_representative"]["yamabe_residual"]),
            0,
        )
        self.assertEqual(
            payload["weyl_covariance"]["weight_ledger"]["u_squared_metric"], 0
        )
        self.assertEqual(
            _fraction(payload["conformized_C2_log"]["logarithmic_coefficient"]),
            Fraction(-199, 60),
        )
        self.assertEqual(payload["cubic_carrier"]["first_completion_order"], 3)

    def test_fv_and_wz_metrics_are_not_identified(self) -> None:
        payload = build()
        self.assertEqual(
            payload["carrier_crosswalk"]["identity_status"],
            "DISTINCT_CARRIERS_NO_IDENTIFICATION",
        )

    def test_independent_cubic_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"][
            "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED"
        ] = True
        with self.assertRaises(Exception):
            validate(payload)

    def test_nonlocal_r2_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"]["NONLOCAL_R2_FORM_FACTOR_COMPUTED"] = True
        with self.assertRaises(Exception):
            validate(payload)

    def test_complete_gamma1_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["decision"]["complete_Gamma1"] = "CERTIFIED"
        with self.assertRaises(Exception):
            validate(payload)

    def test_residual_transfer_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["decision"]["residual_transfer"] = "AUTHORIZED"
        with self.assertRaises(Exception):
            validate(payload)


if __name__ == "__main__":
    unittest.main()
