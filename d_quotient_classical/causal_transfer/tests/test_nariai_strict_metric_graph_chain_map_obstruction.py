from __future__ import annotations

import copy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_strict_metric_graph_chain_map_obstruction import (
    SCHEMA,
    build,
)


class NariaiStrictMetricGraphObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_all_order_killing_witness(self) -> None:
        witness = self.value["all_order_witness"]
        self.assertEqual(witness["K_xi"], "zero section")
        self.assertEqual(witness["normalized_witness_value"], "1")
        self.assertTrue(witness["independent_of_order_and_coefficients"])

    def test_pbw_regression(self) -> None:
        self.assertEqual(
            [entry["rank_gap"] for entry in self.value["pbw_regression"]["screens"]],
            [4, 4, 4, 4, 4],
        )

    def test_fail_closed_flags(self) -> None:
        flags = self.value["flags"]
        self.assertFalse(flags["STRICT_CANONICAL_METRIC_GRAPH_CHAIN_MAP_EXISTS"])
        self.assertFalse(flags["METRIC_BACH_ENDPOINT_CHAIN_EQUIVALENCE"])
        self.assertFalse(flags["NARIAI_GREEN_HOMOTOPY"])

    def test_strict_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_overpromotion(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["flags"]["METRIC_BACH_ENDPOINT_CHAIN_EQUIVALENCE"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)


if __name__ == "__main__":
    unittest.main()
