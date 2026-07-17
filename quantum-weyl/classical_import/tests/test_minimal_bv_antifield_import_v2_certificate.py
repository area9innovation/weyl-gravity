from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from classical_import.minimal_bv_antifield_import_v2_certificate import (
    OUTPUT,
    SCHEMA,
    build,
    validate,
)
from classical_import.verify_minimal_bv_antifield_import_v2 import verify


class MinimalBVAntifieldImportV2Tests(unittest.TestCase):
    def test_import_reproduces_and_is_strict(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, build())
        self.assertEqual(value, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)

    def test_exact_classical_rows_and_scope_projection_are_distinct_checks(self) -> None:
        value = build()
        replay = value["independent_replay"]
        self.assertFalse(replay["producer_proofs_used_as_authority"])
        self.assertEqual(replay["proof_artifact_integrity"], "VERIFIED")
        self.assertEqual(
            replay["filtered_complex_adapter"]["scope_projection"]["status"],
            "DECLARED_GRADED_WINDOW_ENFORCED",
        )
        self.assertGreater(
            replay["filtered_complex_adapter"]["scope_projection"]["projected_monomial_count"],
            0,
        )

    def test_import_does_not_promote_the_minimal_bv_quotient(self) -> None:
        value = build()
        self.assertTrue(value["claim_flags"]["CLASSICAL_ANTIFIELD_EXPORT_IMPORTED"])
        self.assertFalse(value["claim_flags"]["MINIMAL_BV_H04_H14_COMPUTED"])
        self.assertFalse(value["claim_flags"]["QME_RESTORED"])
        self.assertEqual(value["next_gate"], "MINIMAL_BV_H04_H14_WITH_KOSZUL_TATE_ROWS")
        validate(value)


if __name__ == "__main__":
    unittest.main()
