from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.generic_background_ghost_schur_weighted_trace_scale import (
    OUTPUT,
    SCHEMA,
    build,
)
from spectral.euclidean.verify_generic_background_ghost_schur_weighted_trace_scale import (
    main as independent_verify,
)


class GenericBackgroundGhostSchurWeightedTraceScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_order_and_scale_normalization(self) -> None:
        conversion = self.value["exact_conversion"]
        self.assertEqual(conversion["weight_order"], 2)
        self.assertEqual(conversion["dimensionful_scale_power"], 2)
        self.assertEqual(
            conversion["scale_to_weight_order_ratio"],
            {"numerator": 1, "denominator": 1},
        )

    def test_schur_scale_coefficients(self) -> None:
        scale = self.value["exact_conversion"]["scale_coefficients_Ricci_basis"]["log_S"]
        self.assertEqual(scale["R2"], {"numerator": 5, "denominator": 54})
        self.assertEqual(scale["Ric2"], {"numerator": 11, "denominator": 27})

    def test_pole_is_half_residue(self) -> None:
        pole = self.value["exact_conversion"]["pole_coefficients_Ricci_basis"]["log_S"]
        self.assertEqual(pole["R2"], {"numerator": 5, "denominator": 108})
        self.assertEqual(pole["Ric2"], {"numerator": 11, "denominator": 54})

    def test_claim_boundary(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["SCHUR_SCALE_COEFFICIENT_COMPUTED"])
        self.assertFalse(flags["REFERENCE_FINITE_R_K_COMPUTED"])
        self.assertFalse(flags["REFERENCE_FINITE_R_K2_COMPUTED"])
        self.assertFalse(flags["ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
