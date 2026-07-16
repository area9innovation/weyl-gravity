from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian import cyclic_green_realization_import as IMPORT
from lorentzian.cyclic_green_realization_import_certificate import OUTPUT, ROOT, build_certificate


class CyclicGreenRealizationImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads((ROOT / "schema/berger-cyclic-green-realization-import-v1.schema.json").read_text())
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_cyclic_analytic_rows_do_not_promote_green_or_bv_cohomology(self) -> None:
        self.assertTrue(all(self.certificate["independent_exact_checks"].values()))
        self.assertTrue(self.certificate["row_layout"]["added_rows_are_analytic_not_new_cohomology"])
        self.assertFalse(self.certificate["claim_flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"])
        self.assertFalse(self.certificate["claim_flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"])

    def test_mutated_pairing_and_lifecycle_fail_closed(self) -> None:
        source = deepcopy(IMPORT._git_json(IMPORT.CERTIFICATE))
        schema = IMPORT._git_json(IMPORT.SCHEMA)
        extension = json.loads(IMPORT.QUANTUM_EXTENSION_IMPORT.read_text())
        source["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"] = True
        with self.assertRaisesRegex(ValueError, "schema validation|lifecycle"):
            IMPORT.validate_import(source, schema, extension)
        source = IMPORT._git_json(IMPORT.CERTIFICATE)
        source["artifacts"]["analytic_pairing36"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "artifact hash"):
            IMPORT.validate_import(source, schema, extension)


if __name__ == "__main__":
    unittest.main()
