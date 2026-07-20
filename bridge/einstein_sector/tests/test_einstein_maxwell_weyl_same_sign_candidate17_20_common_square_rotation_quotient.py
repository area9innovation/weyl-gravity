import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient import (
    OUTPUT,
    SCHEMA,
    build,
)


class Candidate1720CommonSquareRotationQuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_cartan_square_zero_quotients_are_explicit(self) -> None:
        theorem = self.payload["fixed_occupation_reduction"]
        self.assertEqual(theorem["nonzero_delta_quotient"], "RP^2/SO(3) is one point")
        self.assertIn("closed interval", theorem["zero_delta_quotient"])
        self.assertIn("eta=", theorem["orbit_parameter"])

    def test_candidate17_never_balances(self) -> None:
        row = next(item for item in self.payload["candidate_rows"] if item["candidate_index"] == 17)
        self.assertEqual(
            [item["strict_sign"] for item in row["active_ray_coefficients"]],
            ["NEGATIVE", "NEGATIVE"],
        )
        self.assertTrue(
            self.payload["classification"]["candidate17_common_square_rotation_zero_quotient_always_one_point"]
        )

    def test_candidate20_has_exact_balance_crossing(self) -> None:
        row = next(item for item in self.payload["candidate_rows"] if item["candidate_index"] == 20)
        self.assertEqual(
            [item["strict_sign"] for item in row["active_ray_coefficients"]],
            ["NEGATIVE", "POSITIVE"],
        )
        self.assertTrue(row["balance_witness"]["t20_strictly_positive"])
        self.assertEqual(row["balance_witness"]["rotation_coefficient"], "t20*delta_R2+delta_R4=0")

    def test_scope_remains_one_parity(self) -> None:
        flags = self.payload["classification"]
        self.assertFalse(flags["complete_two_parity_singular_union_quotient_classified"])
        self.assertFalse(flags["occupation_strata_glued"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])

    def test_schema_rejects_erasure_of_balance_divisor(self) -> None:
        mutated = deepcopy(self.payload)
        mutated["classification"]["candidate20_rotation_balance_divisor_nonempty"] = False
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutated)


if __name__ == "__main__":
    unittest.main()
