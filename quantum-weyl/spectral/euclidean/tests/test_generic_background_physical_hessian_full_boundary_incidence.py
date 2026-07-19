from __future__ import annotations

import json
import unittest

from spectral.euclidean.generic_background_physical_hessian_full_boundary_incidence import (
    OUTPUT,
    build,
    validate,
)
from spectral.euclidean.verify_generic_background_physical_hessian_full_boundary_incidence import verify


class GenericPhysicalFullBoundaryIncidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_generated_certificate_is_current(self) -> None:
        self.assertEqual(self.value, build())
        validate(self.value)

    def test_generic_M14_disposition(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED"])
        self.assertTrue(flags["GENERIC_PHYSICAL_M14_DISPOSED"])
        self.assertTrue(flags["GENERIC_PHYSICAL_M14_NONZERO_SCALE_ROW"])
        self.assertEqual(
            self.value["generic_disposition"]["M14"],
            "NONZERO_SCALE_ROW_RENORMALIZED_BY_COMMON_MELLIN_EXTENSION",
        )

    def test_remaining_claims_are_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertFalse(flags["FINITE_LOCAL_MIXED_ROWS_FIXED"])
        self.assertFalse(flags["PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE"])
        self.assertFalse(flags["QME_OR_ANOMALY_STATUS_CHANGED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_independent_consumer(self) -> None:
        verify()


if __name__ == "__main__":
    unittest.main()
