from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from transfer import berger_causal_d_cartan_transfer_import as IMPORT
from transfer.berger_causal_d_cartan_transfer_import_certificate import OUTPUT, ROOT, build_certificate


class BergerCausalDCartanTransferImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads((ROOT / "schema/berger-causal-d-cartan-transfer-import-v1.schema.json").read_text())
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_conditional_theorem_does_not_promote_endpoint(self) -> None:
        self.assertTrue(all(self.certificate["independent_exact_checks"].values()))
        self.assertEqual(self.certificate["endpoint_status"]["conditional_transfer_theorem"], "CERTIFIED")
        self.assertEqual(self.certificate["endpoint_status"]["retained_26_row_causal_green_homotopy"], "NOT_CONSTRUCTED")
        self.assertFalse(self.certificate["claim_flags"]["BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION"])
        self.assertFalse(self.certificate["claim_flags"]["QUANTUM_CLAIM"])

    def test_mutated_formula_and_endpoint_fail_closed(self) -> None:
        source = deepcopy(IMPORT._git_json(IMPORT.CLASSICAL_CERTIFICATE))
        schema = IMPORT._git_json(IMPORT.CLASSICAL_SCHEMA)
        inputs = {name: json.loads(path.read_text()) for name, path in IMPORT.QUANTUM_INPUTS.items()}
        source["arity_two_transfer"]["raw_primitive"] = "+Lambda_s A"
        with self.assertRaisesRegex(ValueError, "formula|schema validation"):
            IMPORT.validate_import(source, schema, inputs)
        source = IMPORT._git_json(IMPORT.CLASSICAL_CERTIFICATE)
        inputs["D_and_causal_reduction"]["conditional_causal_lift"]["endpoint_status"] = "CONSTRUCTED"
        with self.assertRaisesRegex(ValueError, "incomplete or promoted"):
            IMPORT.validate_import(source, schema, inputs)


if __name__ == "__main__":
    unittest.main()
