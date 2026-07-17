from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from local_bv.schema_validation import validate_instance
from transfer.berger_mixed_q3_acceptance_certificate import OUTPUT, SCHEMA, build
from transfer.verify_berger_mixed_q3_acceptance import verify


class BergerMixedQ3AcceptanceTests(unittest.TestCase):
    def test_persisted_exact_receipt_is_accepted_fail_closed(self) -> None:
        value = json.loads(OUTPUT.read_text())
        diagnostics = value["exact_replay"]["diagnostics"]
        self.assertEqual(diagnostics["mixed_arity_three_defect_count"], 0)
        self.assertEqual(diagnostics["typed_q3_graded_symmetry_defect_count"], 0)
        self.assertGreater(diagnostics["localized_mutation_defect_count"], 0)
        self.assertFalse(value["claim_flags"]["RETAINED_MIXED_ELL3_TRANSFER"])
        self.assertFalse(value["claim_flags"]["QUANTUM_CLAIM"])

    def test_persisted_certificate_and_strict_schema(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, build(run_scientific=False))
        self.assertFalse(validate_instance(value, json.loads(SCHEMA.read_text())))

    def test_fast_independent_verifier(self) -> None:
        self.assertEqual(verify(), build(run_scientific=False))

    def test_claim_promotions_and_defect_mutations_are_rejected(self) -> None:
        value = json.loads(OUTPUT.read_text())
        schema = json.loads(SCHEMA.read_text())
        validator = Draft202012Validator(schema)
        for flag in ("RETAINED_MIXED_ELL3_TRANSFER", "REPOSITORY_BV_QME_RESTORED", "QUANTUM_CLAIM"):
            mutant = deepcopy(value)
            mutant["claim_flags"][flag] = True
            self.assertTrue(list(validator.iter_errors(mutant)), flag)
        mutant = deepcopy(value)
        mutant["exact_replay"]["diagnostics"]["mixed_arity_three_defect_count"] = 1
        self.assertTrue(list(validator.iter_errors(mutant)))


if __name__ == "__main__":
    unittest.main()
