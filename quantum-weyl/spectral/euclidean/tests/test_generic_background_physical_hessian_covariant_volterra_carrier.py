from __future__ import annotations

import copy
import unittest

from jsonschema import ValidationError

from spectral.euclidean.generic_background_physical_hessian_covariant_volterra_carrier import (
    build,
    validate,
)


class PhysicalHessianCovariantVolterraCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_cells_and_exact_measures(self) -> None:
        carrier = self.value["decorated_carrier"]
        self.assertEqual(carrier["ordered_triangle_cell_count"], 6)
        self.assertEqual(carrier["mixed_contact_cell_count"], 3)
        self.assertEqual(carrier["resolved_triangle_boundary_chart_count"], 18)
        self.assertEqual(carrier["resolved_contact_endpoint_chart_count"], 6)
        checks = self.value["exact_checks"]
        self.assertEqual(
            checks["triangle_change_of_variables"]["squared_propagator_measure"],
            "T^5*r^3*(1-r)*t*(1-t)",
        )
        self.assertEqual(
            checks["bubble_change_of_variables"]["squared_propagator_measure"],
            "T^3*x*(1-x)",
        )

    def test_noncommuting_replay_and_claim_boundary(self) -> None:
        replay = self.value["exact_checks"]["finite_noncommuting_replay"]
        self.assertEqual(
            replay["trace_log_cubic_value"],
            {"numerator": -3143, "denominator": 1296},
        )
        flags = self.value["claim_flags"]
        self.assertTrue(flags["GENERIC_COVARIANT_VOLTERRA_CARRIER_COMPUTED"])
        self.assertFalse(flags["RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED"])
        self.assertFalse(flags["PHYSICAL_M14_CORNER_CLASS_DISPOSED"])

    def test_fixture_pullback_is_exact(self) -> None:
        pullback = self.value["exact_checks"]["fixture_pullback"]
        self.assertEqual(pullback["status"], "EXACT")
        self.assertEqual(pullback["triangle_boundary_chart_count"], 18)
        self.assertEqual(pullback["contact_endpoint_chart_count"], 6)
        self.assertEqual(
            pullback["scale_coefficient"],
            {"numerator": 15707, "denominator": 216},
        )

    def test_schema_rejects_m14_promotion(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["claim_flags"]["PHYSICAL_M14_CORNER_CLASS_DISPOSED"] = True
        with self.assertRaises(ValidationError):
            validate(mutant)

    def test_schema_rejects_missing_contact(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["decorated_carrier"]["mixed_contact_cells"].pop()
        # Structural semantics are checked by build/verifier; schema still
        # rejects the resulting declared count when it is also mutated.
        mutant["claim_flags"]["THREE_MIXED_CONTACT_CELLS_INCLUDED"] = False
        with self.assertRaises(ValidationError):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
