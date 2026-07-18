from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from anomalies.wess_zumino_extension_preflight import OUTPUT, SCHEMA, build, validate
from anomalies.verify_wess_zumino_extension_preflight import verify


class WessZuminoExtensionPreflightTests(unittest.TestCase):
    def test_two_even_classes_become_exact_in_declared_sector(self) -> None:
        value = build()
        comparison = value["cohomology_comparison"]
        self.assertEqual(comparison["strict_quotient_dimension"], 2)
        self.assertEqual(comparison["extended_quotient_dimension"], 0)
        self.assertEqual(
            value["local_primitives"]["primitive_coordinates"],
            value["local_primitives"]["image_coordinates"],
        )
        matrices = value["doublet_contraction"]["restricted_matrices"]
        self.assertEqual(matrices["Q_squared"], [[0] * 4 for _ in range(4)])
        self.assertEqual(matrices["anticommutator"], matrices["N"])
        self.assertNotEqual(matrices["Qh"], matrices["hQ"])
        self.assertEqual(value["extension"]["dressed_metric_Weyl_weights"]["sum"], 0)

    def test_full_bv_promotion_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["qme_lifecycle"]["residual_transfer"] = "AUTHORIZED"
        with self.assertRaises(ValueError):
            validate(mutant)

    def test_schema_reproduction_and_verifier(self) -> None:
        value = build()
        self.assertEqual(json.loads(OUTPUT.read_text()), value)
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        self.assertEqual(verify(), value)


if __name__ == "__main__":
    unittest.main()
