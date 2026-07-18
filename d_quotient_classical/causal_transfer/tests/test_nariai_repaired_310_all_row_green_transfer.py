from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_repaired_310_all_row_green_transfer import (
    SCHEMA,
    build,
)


class NariaiRepaired310AllRowGreenTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_complete_row_ledger(self) -> None:
        carrier = self.value["carrier"]
        self.assertEqual(carrier["total_rank"], 310)
        self.assertEqual(carrier["degree_ranks"], [15, 140, 140, 15])
        self.assertEqual(carrier["metric_endpoint_total_rank"], 26)
        self.assertEqual(len(carrier["row_coverage"]), 10)
        self.assertEqual(carrier["dropped_rows"], [])

    def test_exact_transfer_and_descent(self) -> None:
        self.assertTrue(all(self.value["exact_checks"].values()))
        self.assertTrue(self.value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"])
        self.assertTrue(self.value["flags"]["NARIAI_METRIC_DESCENT_RECOVERS_ENDPOINT"])

    def test_fail_closed_scope(self) -> None:
        for name in ("OPEN_BACKGROUND_CLASS", "HADAMARD_STATE", "NONLINEAR_EXTENSION", "QUANTUM_CLAIM"):
            self.assertFalse(self.value["flags"][name], name)

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_dropped_row(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["carrier"]["dropped_rows"] = ["h_H1"]
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
