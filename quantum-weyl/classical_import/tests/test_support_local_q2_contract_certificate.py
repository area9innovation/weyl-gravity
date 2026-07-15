from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


IMPORT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = IMPORT_ROOT / "support_local_q2_contract_certificate.py"
SPEC = importlib.util.spec_from_file_location("support_local_q2_contract_certificate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CERTIFICATE)


class SupportLocalQ2ContractCertificateTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_contract_cannot_claim_the_missing_export(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertEqual(
            certificate["result_state"],
            "CONTRACT_READY_AWAITING_CLASSICAL_EXPORT",
        )
        self.assertFalse(certificate["finite_mode_substitution_allowed"])
        self.assertEqual(certificate["checks"]["classical_export_imported"], "NOT_AVAILABLE")
        self.assertEqual(
            certificate["checks"]["full_D_derivation_defect_computed"],
            "NOT_COMPUTED",
        )


if __name__ == "__main__":
    unittest.main()
