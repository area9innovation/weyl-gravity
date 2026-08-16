from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V21_RECONCILIATION.json"
BUILDER = HERE / "build_classical_import_gate_v21_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v21_reconciliation.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("gate_v21_checker", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ClassicalImportGateV21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_generated_current_and_repository_gate_replay(self) -> None:
        subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, check=True)
        self.assertEqual([], self.checker.check())

    def test_m3r_complete_with_m1_and_m4r_open(self) -> None:
        self.assertTrue(self.value["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"])
        self.assertFalse(self.value["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"])
        self.assertEqual(
            ["M1_COMMON_STRICT_SNAPSHOT", "M4R_TYPED_RESIDUAL_CYCLICITY"],
            [item["id"] for item in self.value["minimal_missing_bundle"]],
        )

    def test_gate_remains_fail_closed(self) -> None:
        self.assertEqual("FAIL_CLOSED", self.value["gate_disposition"]["gate_a_status"])
        self.assertEqual(1, self.value["gate_disposition"]["accepted_common_snapshot_hashes"])

    def test_false_locality_promotion_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["HARMONIC_ANALYSIS_SUPPORT_LOCAL"] = True
        self.assertIn("claim promotion HARMONIC_ANALYSIS_SUPPORT_LOCAL", self.checker.check(mutated))

    def test_false_m4r_promotion_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] = True
        self.assertIn("claim promotion M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE", self.checker.check(mutated))

    def test_reintroducing_m3r_missing_item_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["minimal_missing_bundle"].insert(1, {"id": "M3R_TYPED_RESIDUAL_COMPARISON"})
        self.assertIn("typed missing bundle", self.checker.check(mutated))


if __name__ == "__main__":
    unittest.main()
