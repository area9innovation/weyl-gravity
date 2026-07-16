from __future__ import annotations

import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.curved_witness_import_certificate import (
    EXPORT_COMMIT,
    OUTPUT,
    SCHEMA,
    build_certificate,
)


class CurvedWitnessImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_checked_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(SCHEMA.read_text())
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_exact_curved_identities_are_certified(self) -> None:
        checks = self.certificate["independent_exact_checks"]
        self.assertTrue(all(checks.values()))
        self.assertTrue(self.certificate["curved_witness_certified"])
        self.assertIsNone(self.certificate["obstruction_witness"])
        self.assertEqual(
            self.certificate["exact_primitive"]["W34_sha256"],
            "9585c1e9e99efc64f54374a6ea1a95c2975b3ac4832c72e312f5116da4f2a7c3",
        )

    def test_provenance_and_causal_boundary_remain_fail_closed(self) -> None:
        provenance = self.certificate["provenance"]
        self.assertEqual(provenance["export_commit"], EXPORT_COMMIT)
        self.assertTrue(all(item["commit"] == EXPORT_COMMIT for item in provenance["artifacts"]))
        self.assertFalse(self.certificate["green_execution_authorized"])
        self.assertFalse(self.certificate["quantum_execution_authorized"])
        self.assertEqual(
            self.certificate["input_gate_update"]["BERGER_CAUSAL_GREEN_HOMOTOPY"],
            "NOT_CONSTRUCTED",
        )


if __name__ == "__main__":
    unittest.main()
