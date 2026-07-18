from __future__ import annotations

import copy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    SCHEMA,
    build,
)


class NariaiAutomorphismProlongationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_strict_metric_gauge_graph(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual(checks["p0_L0_minus_identity_entries"], 0)
        self.assertEqual(checks["d_aut_L0_minus_L1_K_entries"], 0)
        self.assertTrue(checks["metric_reducibility_graph_exact"])

    def test_two_arrow_complex(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual(checks["M_d_aut_minus_Phi_K_p0_entries"], 0)
        self.assertEqual(checks["P_aut_G_aut_entries"], 0)
        self.assertEqual(checks["P_aut_metric_graph_entries"], 0)

    def test_support_local(self) -> None:
        self.assertTrue(self.value["exact_checks"]["support_local_finite_order"])

    def test_strict_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_cyclic_overpromotion(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["flags"]["CYCLIC_COTANGENT_COMPLETION"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)


if __name__ == "__main__":
    unittest.main()
