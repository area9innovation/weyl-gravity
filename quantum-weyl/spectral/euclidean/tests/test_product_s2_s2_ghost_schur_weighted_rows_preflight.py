from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.product_s2_s2_ghost_schur_weighted_rows_preflight import (
    OUTPUT,
    SCHEMA,
    build,
)
from spectral.euclidean.verify_product_s2_s2_ghost_schur_weighted_rows_preflight import (
    main as independent_verify,
)


class ProductS2S2GhostSchurWeightedRowsPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_exact_pole_replay(self) -> None:
        poles = self.value["exact_pole_replay"]
        self.assertEqual(Fraction(**poles["Res_R_K"]), Fraction(19, 9))
        self.assertEqual(Fraction(**poles["Res_R_K2"]), Fraction(14, 27))

    def test_three_heat_splits_stabilize_candidates(self) -> None:
        settings = self.value["heat_subtraction_settings"]
        self.assertEqual(len(settings), 3)
        r_k = [Decimal(row["base_R_K"]) for row in settings]
        r_k2 = [Decimal(row["base_FP_R_K2"]) for row in settings]
        self.assertLess(max(r_k) - min(r_k), Decimal("1e-12"))
        self.assertLess(max(r_k2) - min(r_k2), Decimal("1e-12"))

    def test_fail_closed_numerical_intervals(self) -> None:
        intervals = self.value["numerical_candidate_intervals"]
        self.assertEqual(
            intervals["status"],
            "NUMERICAL_VALIDATION_INTERVAL_NOT_RIGOROUS_HEAT_REMAINDER_ENCLOSURE",
        )
        flags = self.value["claim_flags"]
        self.assertTrue(flags["PRODUCT_WEIGHTED_R_K_NUMERICAL_CANDIDATE"])
        self.assertTrue(flags["PRODUCT_TRACE_CLASS_REMAINDER_TAILS_RIGOROUSLY_BOUNDED"])
        self.assertFalse(flags["PRODUCT_HEAT_EULER_MACLAURIN_REMAINDER_RIGOROUSLY_BOUNDED"])
        self.assertFalse(flags["PRODUCT_WEIGHTED_R_K_COMPUTED"])
        self.assertFalse(flags["PRODUCT_FINITE_PART_R_K2_COMPUTED"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
