from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from local_bv.schema_validation import validate_instance


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PATH = ROOT / "berger_54_d_causal_import_certificate.py"
SPEC = importlib.util.spec_from_file_location("berger_54_d_causal_import_certificate_test", PATH)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
IMPORTER = sys.modules[CERT.build_import.__module__]


class Berger54DCausalImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d_payload = IMPORTER._git_json(IMPORTER.D_CERTIFICATE)
        cls.d_schema = IMPORTER._git_json(IMPORTER.D_SCHEMA)
        cls.causal_payload = IMPORTER._git_json(IMPORTER.CAUSAL_CERTIFICATE)
        cls.causal_schema = IMPORTER._git_json(IMPORTER.CAUSAL_SCHEMA)
        cls.gauge_payload = IMPORTER._git_json(IMPORTER.GAUGE_CERTIFICATE)

    def test_checked_certificate_reproduces(self) -> None:
        certificate = CERT.build_certificate()
        self.assertEqual(json.loads(CERT.OUTPUT.read_text()), certificate)
        schema = json.loads(
            (ROOT / "schema" / "berger-54-row-D-causal-import-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(certificate, schema))

    def test_all_operator_identities_are_replayed(self) -> None:
        result = CERT.build_certificate()
        self.assertEqual(len(result["independent_operator_checks"]), 7)
        self.assertTrue(all(result["independent_operator_checks"].values()))
        self.assertEqual(result["coverage"]["complete_gauge_fixed_rows"], 54)
        self.assertEqual(result["coverage"]["retained_rows"], 26)

    def test_causal_result_is_conditional_and_endpoint_open(self) -> None:
        result = CERT.build_certificate()
        lift = result["conditional_causal_lift"]
        self.assertEqual(lift["expanded_coefficients"]["sum"], {"ONE_54": 1})
        self.assertEqual(lift["endpoint_status"], "NOT_CONSTRUCTED")
        self.assertFalse(result["quantum_execution_authorized"])

    def test_mutated_D_action_fails_closed(self) -> None:
        forged = deepcopy(self.d_payload)
        forged["D_action"]["matrix"]["entries"][0][2][0][1] = "2"
        with self.assertRaisesRegex(ValueError, "record hash mismatch"):
            IMPORTER.validate_handoff(
                forged, self.d_schema, self.causal_payload,
                self.causal_schema, self.gauge_payload,
            )

    def test_mutated_causal_endpoint_promotion_fails_closed(self) -> None:
        forged = deepcopy(self.causal_payload)
        forged["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"] = True
        with self.assertRaisesRegex(ValueError, "causal endpoint boundary"):
            IMPORTER.validate_handoff(
                self.d_payload, self.d_schema, forged,
                self.causal_schema, self.gauge_payload,
            )

    def test_mutated_causal_dimension_ledger_fails_closed(self) -> None:
        forged = deepcopy(self.causal_payload)
        forged["dimension_ledger"]["retained_endpoint_rows"] = 25
        with self.assertRaisesRegex(ValueError, "dimension ledger"):
            IMPORTER.validate_handoff(
                self.d_payload, self.d_schema, forged,
                self.causal_schema, self.gauge_payload,
            )

    def test_mutated_causal_lift_formula_fails_closed(self) -> None:
        forged = deepcopy(self.causal_payload)
        forged["causal_reduction"]["lifted_formula"] = (
            "Lambda_54,+/-=S-i Lambda_26,+/- p"
        )
        with self.assertRaisesRegex(ValueError, "causal lift formula"):
            IMPORTER.validate_handoff(
                self.d_payload, self.d_schema, forged,
                self.causal_schema, self.gauge_payload,
            )


if __name__ == "__main__":
    unittest.main()
