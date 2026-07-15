from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))
MODULE_PATH = TRANSFER_ROOT / "berger_clock_import_certificate.py"
SPEC = importlib.util.spec_from_file_location("berger_clock_import_certificate_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERTIFICATE
SPEC.loader.exec_module(CERTIFICATE)


class BergerClockImportTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_healthy_background_and_nonzero_momentum_are_retained(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        background = certificate["imported_background"]
        self.assertTrue(background["positive_standard_scalar_kinetic"])
        self.assertTrue(background["bounded_below_quartic"])
        self.assertTrue(background["dominant_energy_condition"])
        self.assertTrue(background["everywhere_timelike_phase_clock"])
        self.assertTrue(certificate["imported_reduced_charge"]["charge_nonzero_on_open_interval"])

    def test_total_D_and_physical_Cartan_run_remain_open(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertEqual(certificate["D_disposition"]["status"], "OPEN")
        self.assertEqual(certificate["setting_verdict"], "INPUT_GATE_BLOCKED")
        self.assertEqual(
            certificate["physical_run_gate"]["route"],
            "BLOCKED_BEFORE_CARTAN_CLASSIFICATION",
        )
        self.assertTrue(
            any("total gravitational-plus-matter" in claim for claim in certificate["not_established"])
        )

    def test_imported_bytes_are_pinned_to_classical_contributions(self) -> None:
        provenance = CERTIFICATE.build_certificate()["provenance"]
        self.assertEqual(len(provenance["background"]["sha256"]), 64)
        self.assertEqual(len(provenance["reduced_charge"]["sha256"]), 64)
        self.assertEqual(provenance["background"]["commit"], provenance["reduced_charge"]["commit"])


if __name__ == "__main__":
    unittest.main()
