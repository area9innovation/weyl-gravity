from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_classical_import_gate_v25_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v25_reconciliation.py"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V25_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V25.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "classical_import_gate_v25_source")
checker = load(CHECKER, "classical_import_gate_v25_checker")


class ClassicalImportGateV25Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current_and_independent_replay(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_m4r_closes_without_passing_gate(self):
        resolution = self.value["m4r_typed_residual_cyclicity_resolution"]
        self.assertEqual(resolution["M4R_TYPED_RESIDUAL_CYCLICITY"], "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6")
        self.assertEqual(self.value["gate_disposition"]["gate_a_status"], "FAIL_CLOSED")

    def test_m1_is_sole_missing_package(self):
        self.assertEqual([item["id"] for item in self.value["minimal_missing_bundle"]], ["M1_COMMON_STRICT_SNAPSHOT"])

    def test_adjoint_projection_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["m4r_typed_residual_cyclicity_resolution"]["projection_equals_inclusion_sharp"] = False
        self.assertTrue(checker.check(value))

    def test_hash_count_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["gate_disposition"]["accepted_common_snapshot_hashes"] = 2
        self.assertTrue(checker.check(value))

    def test_downstream_promotions_fail(self):
        for flag in (
            "M1_COMMON_STRICT_SNAPSHOT_COMPLETE",
            "CLASSICAL_IMPORT_GATE_PASSED",
            "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
            "HADAMARD_STATE_CONSTRUCTED",
            "QME_RESTORED",
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
