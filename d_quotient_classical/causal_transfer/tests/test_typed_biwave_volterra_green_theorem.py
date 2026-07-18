from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer import typed_biwave_volterra_green_theorem as theorem
from d_quotient_classical.causal_transfer import verify_typed_biwave_volterra_green_theorem as independent


class TypedBiwaveVolterraGreenTheoremTest(unittest.TestCase):
    def test_finite_exact_fixture(self) -> None:
        fixture = theorem.exact_operator_fixture()
        self.assertTrue(all(value == 0 for value in fixture["identity_defects"].values()))
        self.assertFalse(fixture["P1_and_P2_commute"])
        self.assertFalse(fixture["P1_and_V_commute"])
        self.assertFalse(fixture["P2_and_V_commute"])

    def test_certificate_and_schema(self) -> None:
        payload, _ = theorem.build()
        theorem.verify(payload)
        schema = json.loads(theorem.SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)

    def test_typed_and_scoped(self) -> None:
        payload, _ = theorem.build()
        self.assertNotEqual(payload["typed_resolvents"]["solution"], payload["typed_resolvents"]["source"])
        self.assertIn("n!", payload["factorial_estimates"]["solution"])
        self.assertIn("n!", payload["factorial_estimates"]["source"])
        self.assertIn("A^sharp", payload["theorem"]["adjoint_reversal"])
        self.assertFalse(payload["flags"]["TRANSVERSE_BACH_FLAT_METRIC_SDR"])
        self.assertFalse(payload["flags"]["HADAMARD_STATE"])

    def test_independent_replay(self) -> None:
        defects = independent._replay_operator_algebra()
        self.assertTrue(all(value == 0 for value in defects.values()))


if __name__ == "__main__":
    unittest.main()
