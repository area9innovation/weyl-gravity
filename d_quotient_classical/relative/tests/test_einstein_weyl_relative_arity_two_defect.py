"""Scoped tests for the compact-product strict relative arity-two defect."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_arity_two_defect as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_arity_two_defect import verify


class RelativeArityTwoDefectTests(unittest.TestCase):
    def test_generated_artifacts_are_current(self) -> None:
        payload = producer.build_payload()
        self.assertEqual(json.loads(producer.PAYLOAD.read_text()), payload)
        self.assertEqual(
            json.loads(producer.CERTIFICATE.read_text()),
            producer.build_certificate(payload),
        )

    def test_independent_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["term_count"], 50854)
        self.assertEqual(sum(bool(value) for value in result["row_defect_counts"]), 15)

    def test_claim_is_fail_closed_before_f2(self) -> None:
        certificate = json.loads(producer.CERTIFICATE.read_text())
        self.assertFalse(certificate["claim_flags"]["STRICT_F1_ARITY_TWO_MORPHISM"])
        self.assertTrue(certificate["claim_flags"]["F2_SOLVE_REQUIRED"])
        self.assertFalse(certificate["claim_flags"]["F2_EXISTS"])
        self.assertFalse(certificate["claim_flags"]["F2_OBSTRUCTED"])
        self.assertFalse(certificate["claim_flags"]["ARITY_THREE_AUTHORIZED"])

    def test_false_zero_promotion_is_schema_rejected(self) -> None:
        certificate = deepcopy(json.loads(producer.CERTIFICATE.read_text()))
        certificate["checks"]["strict_arity_two_defect_zero"] = True
        schema = json.loads(producer.CERTIFICATE_SCHEMA.read_text())
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(certificate)


if __name__ == "__main__":
    unittest.main()
