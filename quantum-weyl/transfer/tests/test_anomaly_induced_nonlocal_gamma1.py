from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from transfer.anomaly_induced_nonlocal_gamma1 import build, validate
from transfer.verify_anomaly_induced_nonlocal_gamma1 import verify


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class AnomalyInducedNonlocalGamma1Tests(unittest.TestCase):
    def test_certificate_builds_and_independently_replays(self) -> None:
        payload = build()
        validate(payload)
        verify()

    def test_exact_coefficients_and_boxr_scheme(self) -> None:
        payload = build()
        solution = [_fraction(value) for value in payload["exact_coefficient_solve"]["solution_vector"]]
        reconstructed = [_fraction(value) for value in payload["exact_coefficient_solve"]["reconstructed_source_vector"]]
        self.assertEqual(solution, [Fraction(199, 120), Fraction(-87, 160), Fraction(29, 120)])
        self.assertEqual(reconstructed, [Fraction(199, 30), Fraction(-87, 20), Fraction()])

    def test_complete_gamma1_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"]["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"] = True
        with self.assertRaises(Exception):
            validate(payload)

    def test_unconditional_green_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["green_operator_contract"]["existence_status"] = "UNCONDITIONAL"
        with self.assertRaises(Exception):
            validate(payload)

    def test_residual_transfer_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["decision"]["residual_transfer"] = "AUTHORIZED"
        with self.assertRaises(Exception):
            validate(payload)


if __name__ == "__main__":
    unittest.main()
