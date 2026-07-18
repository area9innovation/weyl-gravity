from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from transfer.fv_anomaly_action_ricci_sector import build, validate
from transfer.verify_fv_anomaly_action_ricci_sector import verify


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class FVAnomalyActionRicciSectorTests(unittest.TestCase):
    def test_certificate_builds_and_independently_replays(self) -> None:
        payload = build()
        validate(payload)
        verify()

    def test_exact_response_cancellations(self) -> None:
        ledger = build()["exact_cancellation_ledger"]
        self.assertEqual(
            _fraction(ledger["Ecal4_Sigma_cross_response"])
            + _fraction(ledger["Sigma_Delta4_Sigma_cross_response"]),
            0,
        )
        self.assertEqual(
            _fraction(ledger["Ecal4_induced_BoxR_response"])
            + _fraction(ledger["local_R2_BoxR_response"]),
            0,
        )

    def test_rft_specialization_matches_existing_representative(self) -> None:
        payload = build()
        self.assertEqual(
            payload["rft_crosscheck"]["reconstructed_coefficients"],
            payload["rft_crosscheck"]["stored_coefficients"],
        )

    def test_separate_nonlocal_r2_is_not_a_required_datum(self) -> None:
        payload = build()
        self.assertEqual(
            payload["decision"]["independent_nonlocal_R2_form_factor"],
            "NOT_AN_INDEPENDENT_DATUM_IN_DECLARED_FV_CONFORMAL_DECOMPOSITION",
        )
        self.assertFalse(
            payload["claim_flags"]["SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED"]
        )

    def test_separate_nonlocal_r2_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["claim_flags"]["SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED"] = True
        with self.assertRaises(Exception):
            validate(payload)

    def test_complete_gamma1_promotion_is_rejected(self) -> None:
        payload = deepcopy(build())
        payload["decision"]["complete_Gamma1"] = "CERTIFIED"
        with self.assertRaises(Exception):
            validate(payload)


if __name__ == "__main__":
    unittest.main()
