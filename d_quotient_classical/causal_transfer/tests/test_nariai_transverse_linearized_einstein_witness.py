from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer import nariai_transverse_linearized_einstein_witness as producer
from d_quotient_classical.causal_transfer import verify_nariai_transverse_linearized_einstein_witness as independent


class NariaiTransverseLinearizedEinsteinWitnessTest(unittest.TestCase):
    def test_exact_witness(self) -> None:
        witness = producer.exact_witness()
        self.assertEqual(witness["einstein_residuals"], {"tt": "0", "chi_chi": "0", "sphere": "0"})
        self.assertEqual(witness["weyl_contraction_rank"], 4)
        self.assertEqual(witness["delta_C_0202_orthonormal"], "-1")
        self.assertEqual(witness["delta_C_squared"], "-32")

    def test_schema_and_scope(self) -> None:
        payload = producer.build()
        producer.verify(payload)
        schema = json.loads(producer.SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
        self.assertTrue(payload["flags"]["TRANSVERSE_FORMAL_BACH_FLAT_TANGENT"])
        self.assertFalse(payload["flags"]["TRANSVERSE_EXACT_NONLINEAR_BACKGROUND_FAMILY"])
        self.assertFalse(payload["flags"]["TRANSVERSE_METRIC_PARENT_SDR_FIRST_VARIATION"])

    def test_independent_replay(self) -> None:
        replay = independent._independent_replay()
        self.assertEqual(replay["delta_C_0202"], "-1")
        self.assertEqual(replay["delta_C_squared"], "-32")


if __name__ == "__main__":
    unittest.main()
