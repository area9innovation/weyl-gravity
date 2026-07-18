from __future__ import annotations

import json
from decimal import Decimal
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.round_s4_ghost_schur_finite_weighted_traces import (
    OUTPUT,
    SCHEMA,
    build,
)
from spectral.euclidean.verify_round_s4_ghost_schur_finite_weighted_traces import (
    main as independent_verify,
)


class RoundS4GhostSchurFiniteWeightedTracesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_round_sphere_spectrum_and_zero_modes(self) -> None:
        spectrum = self.value["spectral_diagonalization"]
        self.assertEqual(spectrum["S_L_eigenvalue"], "[lambda_ell-4]/[lambda_ell-6]")
        self.assertEqual(self.value["scope"]["mode_domain"], "scalar harmonics ell>=2")
        self.assertIn("five proper-conformal-Killing", self.value["scope"]["excluded_modes"][1])

    def test_exact_finite_rows(self) -> None:
        rows = self.value["exact_finite_rows"]["Delta_weighted_finite_rows"]
        self.assertTrue(rows["R_Delta_K"]["exact"].startswith("-20/9"))
        self.assertTrue(rows["FP_R_Delta_K2"]["exact"].startswith("-(2/3)"))
        self.assertAlmostEqual(float(rows["R_Delta_K"]["decimal"]), -3.0967576144286354)
        self.assertAlmostEqual(float(rows["FP_R_Delta_K2"]["decimal"]), 2.7591028732128106)

    def test_weight_change_and_low_order_split(self) -> None:
        exact = self.value["exact_finite_rows"]
        self.assertEqual(exact["weight_change"]["R_Delta_K_minus_R_B_K"], "-2")
        low = exact["Delta_weighted_finite_rows"]["low_order_renormalized_split"]
        self.assertAlmostEqual(float(low["decimal"]), -4.476309051035041)

    def test_rigorously_enclosed_det3_tail_and_modified_determinant(self) -> None:
        exact = self.value["exact_finite_rows"]
        det3 = exact["canonical_det3_tail"]
        lower = Decimal(det3["lower_endpoint_decimal"])
        upper = Decimal(det3["upper_endpoint_decimal"])
        self.assertLess(lower, upper)
        self.assertAlmostEqual(float((lower + upper) / 2), 0.4981635654196291)
        self.assertTrue(
            det3["certified_common_decimal_prefix"].startswith(
                "0.4981635654196290984312532999414818723861"
            )
        )
        full = exact["full_modified_determinant"]
        self.assertAlmostEqual(float(full["high_precision_decimal"]), -3.9781454856154116)
        self.assertEqual(
            full["status"], "ROUND_S4_WEIGHTED_MODIFIED_DETERMINANT_COMPUTED"
        )

    def test_generic_claim_remains_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["ROUND_S4_R_DELTA_K_COMPUTED"])
        self.assertFalse(flags["GENERIC_BACKGROUND_R_K_COMPUTED"])
        self.assertFalse(flags["GENERIC_MULTIPLICATIVE_ANOMALY_COMPUTED"])
        self.assertTrue(flags["FULL_ROUND_S4_DET3_TAIL_COMPUTED"])
        self.assertTrue(flags["FULL_ROUND_S4_MODIFIED_DETERMINANT_COMPUTED"])
        self.assertFalse(flags["FULL_GENERIC_SCHUR_DETERMINANT_COMPUTED"])
        self.assertEqual(
            self.value["generic_missing_input_theorem"]["status"],
            "MINIMAL_MISSING_GLOBAL_CARRIER_THEOREM",
        )

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
