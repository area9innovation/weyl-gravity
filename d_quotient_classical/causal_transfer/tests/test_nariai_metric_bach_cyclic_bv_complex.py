from __future__ import annotations

import copy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_metric_bach_cyclic_bv_complex import (
    SCHEMA,
    build,
)


class NariaiMetricBachCyclicBVComplexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_noether_identities(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual(checks["B_K_defect_entries"], 0)
        self.assertEqual(checks["Ksharp_B_defect_entries"], 0)

    def test_four_row_cyclic_complex(self) -> None:
        checks = self.value["exact_checks"]
        self.assertTrue(checks["abstract_Q_squared_mod_Noether"])
        self.assertTrue(checks["abstract_odd_cyclicity"])
        self.assertTrue(checks["action_pairing_reconciled"])

    def test_typed_pairings(self) -> None:
        pairing = self.value["action_pairing"]
        self.assertTrue(pairing["tensor_gram_not_applied_twice"])
        self.assertEqual(pairing["field_equation_pairing"]["shape"], [9, 9])
        self.assertEqual(pairing["ghost_identity_pairing"]["shape"], [4, 4])

    def test_strict_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_relative_overpromotion(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["flags"]["RELATIVE_EQUATION_IDENTITY_CONE"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)


if __name__ == "__main__":
    unittest.main()
