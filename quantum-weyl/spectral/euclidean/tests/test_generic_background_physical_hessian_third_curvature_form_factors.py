from __future__ import annotations

import json
import unittest

from spectral.euclidean.generic_background_physical_hessian_third_curvature_form_factors import (
    OUTPUT,
    validate,
)
from spectral.euclidean.verify_generic_background_physical_hessian_third_curvature_form_factors import (
    verify,
)


class GenericPhysicalThirdCurvatureFormFactorsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_emitted_certificate_is_valid(self) -> None:
        validate(self.value)

    def test_five_carrier_ten_dimensional_quotient(self) -> None:
        self.assertEqual(len(self.value["carrier_functions"]), 5)
        self.assertEqual(
            sum(row["orientation_count"] for row in self.value["carrier_functions"]),
            11,
        )
        self.assertEqual(self.value["quotient_ledger"]["quotient_dimension"], 10)
        self.assertEqual(self.value["quotient_ledger"]["status"], "EXACT")

    def test_claim_boundary_is_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["PHYSICAL_HESSIAN_MELLIN_MS_FORM_FACTOR_REPRESENTATIVE_COMPUTED"])
        self.assertFalse(flags["ABSOLUTE_FINITE_C2_NORMALIZATION_FIXED"])
        self.assertFalse(flags["FULL_BV_FORM_FACTORS_COMPUTED"])
        self.assertFalse(flags["COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED"])
        self.assertFalse(flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"])
        self.assertFalse(flags["QME_OR_ANOMALY_STATUS_CHANGED"])
        self.assertFalse(flags["RESIDUAL_TRANSFER_AUTHORIZED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_independent_consumer(self) -> None:
        verify()


if __name__ == "__main__":
    unittest.main()
