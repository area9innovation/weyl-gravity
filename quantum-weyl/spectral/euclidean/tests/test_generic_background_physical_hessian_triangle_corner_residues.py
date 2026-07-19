from __future__ import annotations

import json
import unittest

from spectral.euclidean.generic_background_physical_hessian_triangle_corner_residues import (
    OUTPUT,
    build,
    validate,
)
from spectral.euclidean.verify_generic_background_physical_hessian_triangle_corner_residues import verify


class GenericPhysicalTriangleCornerResiduesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_generated_certificate_is_current(self) -> None:
        self.assertEqual(self.value, build())
        validate(self.value)

    def test_all_generic_rows_are_present(self) -> None:
        self.assertEqual(len(self.value["channel_rows"]), 11)
        self.assertTrue(
            self.value["claim_flags"]["GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED"]
        )
        self.assertEqual(
            self.value["regressions"]["symmetric_obstruction_rows_matched"], 11
        )

    def test_claim_boundary_remains_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertFalse(flags["FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED"])
        self.assertFalse(flags["GENERIC_PHYSICAL_M14_DISPOSED"])
        self.assertFalse(flags["QME_OR_ANOMALY_STATUS_CHANGED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_independent_consumer(self) -> None:
        verify()


if __name__ == "__main__":
    unittest.main()
