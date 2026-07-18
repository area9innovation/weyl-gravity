from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_automorphism_cyclic_bach_extension import (
    SCHEMA,
    build,
)


class NariaiAutomorphismCyclicBachExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_exact_cyclic_complex(self) -> None:
        checks = self.value["checks"]
        self.assertTrue(checks["abstract_Q_squared_mod_certified_relations"])
        self.assertTrue(checks["abstract_odd_cyclicity"])
        self.assertEqual(checks["M_daut_minus_Phi_Kp0_entries"], 0)
        self.assertEqual(checks["B_Kp0_entries"], 0)

    def test_metric_graph_and_pairing(self) -> None:
        checks = self.value["checks"]
        self.assertTrue(checks["metric_graph_chain_map_mod_certified_relations"])
        self.assertTrue(checks["metric_pairing_pullback_mod_retract_relations"])
        self.assertEqual(checks["P_metric_graph_entries"], 0)

    def test_carrier_and_action(self) -> None:
        self.assertEqual(self.value["carrier"]["total_rank"], 288)
        self.assertTrue(self.value["action"]["no_fitted_cotangent_rows"])
        self.assertTrue(self.value["flags"]["ACTION_DERIVED_MIDDLE"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_green_overpromotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["NARIAI_GREEN_HOMOTOPY"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
