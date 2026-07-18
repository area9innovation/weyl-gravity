from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.tt_hessian_dictionary_receiver import ROOT, synthetic_payload, validate_tt_hessian_dictionary
from spectral.euclidean.tt_hessian_dictionary_receiver_readiness import OUTPUT, SCHEMA, build, mutation_receipts, validate_claim_boundary
from spectral.euclidean.verify_tt_hessian_dictionary_receiver_readiness import verify


class TTHessianDictionaryReceiverTests(unittest.TestCase):
    def test_synthetic_complete_contract_is_accepted(self) -> None:
        payload = synthetic_payload()
        receipt = validate_tt_hessian_dictionary(payload, repository_root=ROOT, expected_classical_commit="0" * 40)
        self.assertEqual(receipt["status"], "SEMANTIC_RECEIVER_ACCEPTED")
        self.assertEqual(receipt["kappa"], {"numerator": 1, "denominator": 2})

    def test_all_semantic_mutations_are_rejected(self) -> None:
        payload = synthetic_payload()
        self.assertTrue(all(row["rejected"] for row in mutation_receipts(payload, "0" * 40)))

    def test_claim_boundary_rejects_physical_input_promotion(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["PHYSICAL_TT_DICTIONARY_INPUT_SUPPLIED"] = True
        with self.assertRaisesRegex(ValueError, "claim boundary"):
            validate_claim_boundary(mutant)

    def test_schema_and_independent_verifier(self) -> None:
        value = build()
        self.assertEqual(json.loads(OUTPUT.read_text()), value)
        self.assertEqual(verify(), value)
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        mutant = deepcopy(value)
        mutant["claim_flags"]["QME_DISPOSITION"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
