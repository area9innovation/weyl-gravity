from __future__ import annotations

import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.metric_equal_connection_factor_screen import evaluate_screen
from lorentzian.metric_equal_connection_factor_screen_certificate import (
    OUTPUT,
    SCHEMA,
    build_certificate,
)


class MetricEqualConnectionFactorScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(SCHEMA.read_text())
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_normalized_obstruction_is_exact_and_scoped(self) -> None:
        screen = self.certificate["screen"]
        self.assertTrue(all(screen["exact_checks"].values()))
        self.assertEqual(screen["normalized_dual_witness"]["value"], "1")
        self.assertEqual(screen["normalized_dual_witness"]["representative"], "-p0*p3*u**2")
        self.assertTrue(
            self.certificate["claim_flags"]["BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORTED"]
        )
        self.assertTrue(screen["exact_checks"]["A10_equals_Box2_squared_plus_V2"])
        self.assertTrue(screen["exact_checks"]["dedicated_lower_by_two_quantum_import_bound"])
        self.assertTrue(screen["exact_checks"]["metric_cone_bordered_determinant_replayed"])
        self.assertTrue(
            self.certificate["claim_flags"]["BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO_IMPORTED"]
        )
        self.assertEqual(self.certificate["upstream_next_gate"], "BERGER_LOWER_BY_TWO_CAUSAL_RESOLVENT")
        self.assertEqual(
            self.certificate["claim_flags"]["UNEQUAL_SUBPRINCIPAL_FACTOR_ANSATZ"],
            "OPEN",
        )
        self.assertFalse(
            self.certificate["claim_flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"]
        )
        self.assertEqual(
            self.certificate["next_gate"],
            "BERGER_HYBRID_RETAINED_CAUSAL_CHAIN_HOMOTOPY",
        )

    def test_pinned_replay_is_deterministic(self) -> None:
        first = evaluate_screen()
        second = evaluate_screen()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
