from __future__ import annotations

import copy
import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_polar_ungauged_bv_residual_descent import (
    DEFAULT_OUTPUT,
    _generic_obstruction,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_ungauged_bv_residual_descent import (
    verify_payload,
)


class PolarUngaugedBVResidualDescentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(DEFAULT_OUTPUT.read_text())

    def test_exact_generic_obstruction(self) -> None:
        obstruction = _generic_obstruction()
        self.assertEqual(obstruction["determinant_D"], "-9*lambda/2")
        self.assertEqual(obstruction["rank_for_every_physical_lambda_ell_at_least_2"], 2)

    def test_generator_and_independent_verifier(self) -> None:
        verify_certificate()
        verify_payload(self.payload)

    def test_false_cyclic_promotion_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["classification"]["strict_identity_cyclic_BV_lift_exists"] = True
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(mutated, verify_files=False)

    def test_stabilizer_gauge_mutation_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["global_residual_authority"]["absolute_stabilizer_gauge_quotient"] = "CERTIFIED"
        with self.assertRaises(jsonschema.ValidationError):
            verify_payload(mutated, verify_files=False)

    def test_charge_deletion_mutation_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["charge_and_large_gauge"]["Wilson_line_W_x"] = "deleted as local gauge"
        with self.assertRaises(AssertionError):
            verify_payload(mutated, verify_files=False)


if __name__ == "__main__":
    unittest.main()
