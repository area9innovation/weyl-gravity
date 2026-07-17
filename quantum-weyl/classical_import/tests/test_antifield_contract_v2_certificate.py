from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from classical_import.antifield_contract_v2_certificate import (
    OUTPUT,
    SCHEMA,
    build,
    validate,
)
from classical_import.verify_antifield_contract_v2 import verify


class AntifieldContractV2CertificateTests(unittest.TestCase):
    def test_certificate_reproduces_and_is_strict(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, build())
        self.assertEqual(value, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)

    def test_contract_stays_fail_closed(self) -> None:
        value = build()
        flags = value["claim_flags"]
        self.assertTrue(flags["ANTIFIELD_EXPORT_V2_RECEIVER_READY"])
        self.assertTrue(flags["DECLARED_GRADED_SCOPE_ENFORCED"])
        self.assertTrue(flags["INDEPENDENT_FILTRATION_REPLAY_READY"])
        self.assertTrue(flags["IMPORT_STATUS_DELEGATED_TO_SEPARATE_RECEIPT"])
        self.assertFalse(flags["FULL_BV_G2_COMPLETE"])
        self.assertFalse(flags["QME_RESTORED"])
        validate(value)

    def test_resource_policy_is_hash_triggered(self) -> None:
        policy = build()["resource_policy"]
        self.assertIn("differential_hash", policy["quotient_rerun_key"])
        self.assertIn("AFN0_basis_manifest_hashes", policy["quotient_rerun_key"])
        self.assertIn("otherwise", policy)


if __name__ == "__main__":
    unittest.main()
