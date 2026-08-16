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
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V20_RECONCILIATION.json"
BUILDER = HERE / "build_classical_import_gate_v20_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v20_reconciliation.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("gate_v20_checker", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ClassicalImportGateV20Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.checker = load_checker()

    def test_generated_current(self) -> None:
        subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, check=True)

    def test_repository_gate_replays(self) -> None:
        self.assertEqual([], self.checker.check())

    def test_m4l_is_complete_and_m4r_open(self) -> None:
        self.assertTrue(self.value["claim_flags"]["M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE"])
        self.assertFalse(self.value["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"])
        self.assertEqual(
            ["M1_COMMON_STRICT_SNAPSHOT", "M3R_TYPED_RESIDUAL_COMPARISON", "M4R_TYPED_RESIDUAL_CYCLICITY"],
            [item["id"] for item in self.value["minimal_missing_bundle"]],
        )

    def test_gate_remains_fail_closed(self) -> None:
        self.assertEqual("FAIL_CLOSED", self.value["gate_disposition"]["gate_a_status"])
        self.assertEqual(1, self.value["gate_disposition"]["accepted_common_snapshot_hashes"])

    def test_false_gate_promotion_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertIn("claim promotion CLASSICAL_IMPORT_GATE_PASSED", self.checker.check(mutated))

    def test_unsplit_m4_mutation_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["minimal_missing_bundle"][-1]["id"] = "M4_FULL_CYCLIC_PAIRING"
        self.assertIn("typed missing bundle", self.checker.check(mutated))


if __name__ == "__main__":
    unittest.main()
