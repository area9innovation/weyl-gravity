from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_extra_branch_preflight import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate
from bridge.einstein_sector.verify_einstein_maxwell_weyl_extra_branch_preflight import verify_certificate as verify_independently


class ExtraBranchPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_canonical_quotient_not_complement(self) -> None:
        contract = self.payload["canonical_object_contract"]
        self.assertTrue(contract["definition_is_canonical_quotient_not_complement"])
        self.assertTrue(contract["symplectic_complement_is_not_the_definition"])

    def test_result_kinds_and_fail_closed_state(self) -> None:
        self.assertEqual(len(self.payload["result_kind_separation"]), 5)
        classification = self.payload["classification"]
        self.assertFalse(classification["any_extra_solution_class_certified"])
        self.assertFalse(classification["extra_branch_pairing_computed"])

    def test_first_block_and_boundaries(self) -> None:
        self.assertEqual(self.payload["first_computation"]["block"], "generic axial ell>=2 at symbolic lambda and k")
        self.assertFalse(self.payload["function_space_and_gauge_contract"]["bounded_in_time_restriction"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
