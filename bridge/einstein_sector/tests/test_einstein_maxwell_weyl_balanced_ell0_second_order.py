from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_balanced_ell0_second_order import (
    verify_certificate as verify_independently,
)


class BalancedEll0SecondOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))

    def test_complete_extension(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["complete_second_order_extension_constructed"])
        self.assertTrue(classification["all_nonzero_frequency_homogeneous_channels_solved"])
        self.assertTrue(classification["all_ell2_ell4_channels_solved_with_explicit_action_inverse"])
        self.assertTrue(self.payload["second_order_correction"]["all_operator_remainders_zero"])

    def test_zero_frequency_homogeneous_cancellation(self) -> None:
        self.assertEqual(
            self.payload["homogeneous_channels"]["combined_zero"]["source_rows_E00_E11_E22_Maxwell1"],
            ["0", "0", "0", "0"],
        )

    def test_boundaries(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["remaining_adjoint_obstruction_exhibited"])
        self.assertFalse(classification["causal_or_quantum_claim"])

    def test_schema_and_fast_verifiers(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        verify_certificate()
        verify_independently()


if __name__ == "__main__":
    unittest.main()
