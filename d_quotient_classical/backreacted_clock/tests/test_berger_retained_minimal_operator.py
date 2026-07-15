from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.berger_retained_minimal_operator import (
    BergerRetainedMinimalOperatorPreflight,
)


class BergerRetainedMinimalOperatorPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = BergerRetainedMinimalOperatorPreflight.build().payload

    def test_layout_and_exact_rows(self) -> None:
        self.assertEqual(self.payload["layout_ref"]["component_count"], 26)
        checks = self.payload["exact_checks"]
        self.assertTrue(checks["K_spatial_coefficients_complete"])
        self.assertTrue(checks["minus_K_spatial_sharp_coefficients_complete"])
        self.assertTrue(checks["matter_hessian_covariant_coefficients_complete"])

    def test_principal_operator(self) -> None:
        checks = self.payload["exact_checks"]
        self.assertTrue(checks["Bach_fourth_order_principal_complete"])
        self.assertTrue(checks["principal_formal_self_adjointness"])
        self.assertTrue(checks["principal_Bach_K_identity"])
        self.assertTrue(checks["principal_matter_K_identity"])
        self.assertEqual(checks["generic_Bach_principal_rank"], 5)

    def test_nonconformally_flat_guard(self) -> None:
        guard = self.payload["nonconformally_flat_guard"]
        self.assertTrue(guard["background_Weyl_nonzero"])
        self.assertTrue(guard["background_Bach_nonzero"])
        self.assertFalse(guard["round_cylinder_lower_order_hessian_reused"])

    def test_parent_gate_remains_open(self) -> None:
        flags = self.payload["flags"]
        self.assertFalse(flags["retained_Bach_lower_order_PBW_complete"])
        self.assertFalse(flags["retained_q1_coefficients_complete"])
        self.assertFalse(flags["retained_q1_squared_verified"])
        self.assertFalse(flags["retained_cyclicity_verified"])
        self.assertFalse(flags["BERGER_RETAINED_MINIMAL_OPERATOR"])
        self.assertEqual(
            self.payload["next_gate"], "BERGER_LINEARIZED_BACH_PBW_EXPANSION"
        )


if __name__ == "__main__":
    unittest.main()
