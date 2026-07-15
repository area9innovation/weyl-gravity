from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))
MODULE_PATH = TRANSFER_ROOT / "arity_three_cartan_certificate.py"
SPEC = importlib.util.spec_from_file_location("arity_three_cartan_certificate_test_module", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERTIFICATE
SPEC.loader.exec_module(CERTIFICATE)


class ArityThreeCartanCertificateTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_direct_exchange_and_obstruction_branches_are_live(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertEqual(certificate["direct_q3_fixture"]["classification"], "EXACT_CORRECTION")
        self.assertTrue(certificate["direct_q3_fixture"]["correction_identity"])
        self.assertTrue(certificate["exchange_fixture"]["exchange_nonzero"])
        self.assertEqual(
            certificate["obstruction_fixture"]["classification"],
            "NONTRIVIAL_OBSTRUCTION",
        )

    def test_physical_q3_and_lower_run_remain_input_gated(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertEqual(certificate["setting_verdict"], "INPUT_GATE_BLOCKED")
        self.assertTrue(
            certificate["input_gate"]["support_local_classical_bv_q3"].startswith("NOT_AVAILABLE")
        )
        self.assertTrue(
            any("conformal-gravity q3" in claim for claim in certificate["not_established"])
        )


if __name__ == "__main__":
    unittest.main()
