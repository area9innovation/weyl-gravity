import json
import unittest

from cylinder.afn0_restriction_preflight import afn0_restriction_preflight
from cylinder.afn0_restriction_preflight_certificate import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_certificate,
)
from local_bv.schema_validation import validate_instance


class AfnZeroCylinderRestrictionPreflightTests(unittest.TestCase):
    def test_background_is_exactly_conformally_flat(self) -> None:
        payload = afn0_restriction_preflight()
        self.assertEqual(payload["background"]["scalar_curvature"], 6)
        self.assertEqual(payload["background"]["weyl_nonzero_component_count"], 0)
        self.assertEqual(
            payload["background"]["curvature_audit"],
            {
                "riemann_product_identity": "R_ijkl=g_ik g_jl-g_il g_jk; time components zero",
                "ricci_product_identity": "Ric_ij=2 g_ij; time components zero",
                "riemann_squared": 12,
                "ricci_squared": 12,
                "scalar_curvature": 6,
                "euler_density": 0,
            },
        )

    def test_quadratic_weyl_densities_start_at_second_order(self) -> None:
        ledger = afn0_restriction_preflight()["expansion_ledger"]
        for class_id in ("CT_C2", "CT_C_DUAL_C"):
            self.assertEqual(ledger[class_id]["order_h0"], "ZERO_FROM_C_GBAR_ZERO")
            self.assertEqual(ledger[class_id]["order_h1"], "ZERO_FROM_C_GBAR_ZERO")
        self.assertIn("C1(h)", ledger["CT_C2"]["order_h2"])
        self.assertIn("star_C1", ledger["CT_C_DUAL_C"]["order_h2"])

    def test_parity_support_is_diagonal_but_normalization_is_withheld(self) -> None:
        parity = afn0_restriction_preflight()["parity_support"]
        self.assertEqual(
            parity["support_matrix"],
            [["ALLOWED_NONZERO", "ZERO_BY_PARITY"], ["ZERO_BY_PARITY", "ALLOWED_NONZERO"]],
        )
        self.assertIsNone(parity["normalization_matrix"])
        self.assertEqual(
            parity["normalization_status"],
            "UNDEFINED_PENDING_FROZEN_REPRESENTATIVE_VECTORS_AND_PI_CL",
        )

    def test_projection_stays_fail_closed(self) -> None:
        payload = afn0_restriction_preflight()
        self.assertEqual(payload["local_to_cylinder_map_status"], "NOT_COMPUTED")
        self.assertEqual(payload["residual_projection_status"], "BLOCKED_FAIL_CLOSED")
        self.assertTrue(all(payload["projection_blockers"].values()))

    def test_schema_and_checked_in_certificate_reproduce(self) -> None:
        certificate = build_certificate()
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertFalse(validate_instance(certificate, schema))
        self.assertEqual(json.loads(OUTPUT_PATH.read_text(encoding="utf-8")), certificate)


if __name__ == "__main__":
    unittest.main()
