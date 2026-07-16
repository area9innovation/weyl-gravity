from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PATH = ROOT / "berger_54_row_local_d_import_certificate.py"
SPEC = importlib.util.spec_from_file_location(
    "berger_54_row_local_d_import_certificate_test", PATH
)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
IMPORT = sys.modules[CERT.build_import.__module__]


class Berger54RowLocalDImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = IMPORT._git_json(IMPORT.CERTIFICATE_RELATIVE)
        cls.schema = IMPORT._git_json(IMPORT.SCHEMA_RELATIVE)
        cls.gauge_fixed = IMPORT._git_json(IMPORT.GAUGE_FIXED_RELATIVE)

    def test_checked_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(CERT.OUTPUT.read_text()), CERT.build_certificate())

    def test_complete_D_action_and_equivariance_are_imported(self) -> None:
        result = CERT.build_certificate()
        self.assertEqual(result["coverage"]["total_rows"], 54)
        self.assertTrue(result["coverage"]["local_D_action_complete"])
        self.assertTrue(result["coverage"]["unary_equivariance_complete"])
        self.assertTrue(result["coverage"]["contraction_equivariance_complete"])
        self.assertTrue(result["coverage"]["cyclicity_complete"])

    def test_G2_and_ND2_remain_fail_closed_without_q2(self) -> None:
        result = CERT.build_certificate()
        self.assertFalse(
            result["generality_assessment"]["promotion_to_G2_authorized"]
        )
        self.assertEqual(
            result["nd2_gate"]["support_local_classical_binary_q2"],
            "NOT_AVAILABLE",
        )
        self.assertEqual(
            result["nd2_gate"]["arity_two_Cartan_source"], "INPUT_BLOCKED"
        )
        self.assertFalse(result["nd2_gate"]["physical_execution_authorized"])

    def test_mutations_fail_closed(self) -> None:
        forged = deepcopy(self.payload)
        forged["D_action"]["matrix"]["entries"][0][2][0][1] = "2"
        with self.assertRaisesRegex(ValueError, "record hash mismatch"):
            IMPORT.validate_import(forged, self.schema, self.gauge_fixed)

        forged = deepcopy(self.payload)
        forged["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] = True
        with self.assertRaisesRegex(ValueError, "claim boundary"):
            IMPORT.validate_import(forged, self.schema, self.gauge_fixed)

        forged = deepcopy(self.payload)
        forged["dependency_refs"]["gauge_fixed_54_row_unary"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "dependency"):
            IMPORT.validate_import(forged, self.schema, self.gauge_fixed)

        forged = deepcopy(self.payload)
        forged["row_layout"]["row_ids"] = forged["row_layout"]["row_ids"][:-1]
        with self.assertRaisesRegex(ValueError, "row ledger"):
            IMPORT.validate_import(forged, self.schema, self.gauge_fixed)


if __name__ == "__main__":
    unittest.main()
