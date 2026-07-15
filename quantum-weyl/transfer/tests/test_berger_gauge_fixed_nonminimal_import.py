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
PATH = ROOT / "berger_gauge_fixed_nonminimal_import_certificate.py"
SPEC = importlib.util.spec_from_file_location("berger_gauge_fixed_nonminimal_import_certificate_test", PATH)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
IMPORT = sys.modules[CERT.build_import.__module__]


class BergerGaugeFixedNonminimalImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = IMPORT._git_json(IMPORT.CERTIFICATE_RELATIVE)
        cls.schema = IMPORT._git_json(IMPORT.SCHEMA_RELATIVE)

    def test_checked_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(CERT.OUTPUT.read_text()), CERT.build_certificate())

    def test_complete_unary_prerequisite_only(self) -> None:
        result = CERT.build_certificate()
        self.assertTrue(result["coverage"]["gauge_fixed_classical_unary_complete"])
        self.assertEqual(result["coverage"]["total_rows"], 54)
        self.assertTrue(result["nd2_gate"]["unary_nonminimal_prerequisite_satisfied"])
        self.assertFalse(result["nd2_gate"]["physical_execution_authorized"])

    def test_q2_and_D_remain_fail_closed(self) -> None:
        gate = CERT.build_certificate()["nd2_gate"]
        self.assertEqual(gate["support_local_classical_binary_q2"], "NOT_AVAILABLE")
        self.assertEqual(gate["local_D_action_and_equivariance"], "NOT_AVAILABLE")
        self.assertEqual(gate["next_gate"], "IMPORT_SUPPORT_LOCAL_Q2_AND_D_ACTION")

    def test_tampered_map_and_promotion_are_rejected(self) -> None:
        forged = deepcopy(self.payload)
        forged["classical_unary_q1"]["matrix"]["entries"][0][2][0][1] = "2"
        with self.assertRaisesRegex(ValueError, "record hash mismatch"):
            IMPORT.validate_import(forged, self.schema)
        forged = deepcopy(self.payload)
        forged["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] = True
        with self.assertRaisesRegex(ValueError, "boundary was crossed"):
            IMPORT.validate_import(forged, self.schema)


if __name__ == "__main__":
    unittest.main()
