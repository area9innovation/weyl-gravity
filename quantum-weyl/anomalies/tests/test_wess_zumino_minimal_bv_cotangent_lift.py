from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from anomalies.wess_zumino_minimal_bv_cotangent_lift import OUTPUT, SCHEMA, build, validate
from anomalies.verify_wess_zumino_minimal_bv_cotangent_lift import verify


class WessZuminoMinimalBVCotangentLiftTests(unittest.TestCase):
    def test_extended_differential_and_quartet_are_exact(self) -> None:
        value = build()
        self.assertTrue(value["exact_checks"]["delta_squared_zero_on_all_atoms"])
        self.assertTrue(value["exact_checks"]["delta_gamma_anticommutator_zero_on_all_atoms"])
        self.assertTrue(value["exact_checks"]["Q_squared_zero_on_all_atoms"])
        self.assertTrue(value["exact_checks"]["exact_component_gradings_verified"])
        self.assertEqual(
            value["contractible_quartet"]["anticommutator"],
            value["contractible_quartet"]["number_operator"],
        )
        self.assertEqual(
            value["dressed_cotangent_change"]["Weyl_Koszul_Tate_row"],
            "delta omega_star = tau_hat_star",
        )

    def test_wrong_cotangent_sign_and_qme_promotion_fail_closed(self) -> None:
        mutant = deepcopy(build())
        mutant["extended_rows"]["Lie_omega_star"]["delta"]["terms"][-1]["coefficient"] = 1
        with self.assertRaises(ValueError):
            validate(mutant)
        mutant = deepcopy(build())
        mutant["qme_lifecycle"]["residual_transfer"] = "AUTHORIZED"
        with self.assertRaises(ValueError):
            validate(mutant)

    def test_schema_reproduction_and_independent_verifier(self) -> None:
        value = build()
        self.assertEqual(json.loads(OUTPUT.read_text()), value)
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        self.assertEqual(verify(), value)


if __name__ == "__main__":
    unittest.main()
