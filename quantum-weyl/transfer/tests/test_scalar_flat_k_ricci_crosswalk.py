from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from transfer.scalar_flat_k_ricci_crosswalk import OUTPUT, SCHEMA, build, validate
from transfer.verify_scalar_flat_k_ricci_crosswalk import verify


class ScalarFlatKRicciCrosswalkTests(unittest.TestCase):
    def test_linear_normalization_and_cubic_order(self) -> None:
        value = build()
        self.assertEqual(
            value["linear_crosswalk"]["normalized_linear_coefficient"],
            {"numerator": 1, "denominator": 1},
        )
        self.assertEqual(
            value["linear_crosswalk"]["identity"],
            "K_munu=Ric_munu+O(curvature^2)",
        )
        self.assertEqual(
            value["cubic_order_counting"]["first_replacement_error_order"], 4
        )

    def test_all_five_carriers_are_routed(self) -> None:
        target = build()["five_carrier_target"]
        self.assertEqual(target["carrier_ids"], ["I10", "I24", "I25", "I28", "I29"])
        self.assertEqual(
            target["triangle_sector_routing"][-1]["possible_repository_carriers"],
            ["I10", "I24", "I25", "I28", "I29"],
        )
        self.assertEqual(target["projection_status"], "NOT_COMPUTED")

    def test_semantic_mutations_are_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["linear_crosswalk"]["normalized_linear_coefficient"] = {
            "numerator": -1,
            "denominator": 1,
        }
        with self.assertRaises(ValueError):
            validate(mutant)
        mutant = deepcopy(build())
        mutant["five_carrier_target"]["triangle_sector_routing"][-1][
            "possible_repository_carriers"
        ] = ["I10"]
        with self.assertRaises(ValueError):
            validate(mutant)

    def test_schema_is_strict(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(build())
        mutant = deepcopy(build())
        mutant["extra"] = True
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(mutant)))

    def test_certificate_and_independent_replay(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
