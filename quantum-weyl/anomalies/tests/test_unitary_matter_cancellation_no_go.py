from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from anomalies.unitary_matter_cancellation_no_go import OUTPUT, SCHEMA, build, validate
from anomalies.verify_unitary_matter_cancellation_no_go import verify


class UnitaryMatterCancellationNoGoTests(unittest.TestCase):
    def test_exact_empty_cone_certificate(self) -> None:
        value = build()
        self.assertEqual(
            value["cancellation_equations"]["integer_rows"],
            [[4776, 6, 18, 36, 72], [-3132, -2, -11, -22, -124]],
        )
        self.assertEqual(value["classification"]["solution_set"], "EMPTY")
        self.assertFalse(value["classification"]["integer_search_required"])

    def test_mutation_is_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["separating_witnesses"][0]["matter_generator_values"][
            "real_conformal_scalar"
        ]["numerator"] = -1
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
