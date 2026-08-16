from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_classical_import_gate_v26_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v26_reconciliation.py"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V26_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V26.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "classical_import_gate_v26_source")
checker = load(CHECKER, "classical_import_gate_v26_checker")


class ClassicalImportGateV26Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current_and_independent_replay(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_three_ordered_packages_preserve_one_gate_bundle(self):
        self.assertEqual([row["id"] for row in self.value["minimal_missing_bundle"]], ["M1_COMMON_STRICT_SNAPSHOT"])
        self.assertEqual([row["status"] for row in self.value["m1_common_snapshot_preflight_resolution"]["work_packages"]], ["OPEN", "OPEN_AFTER_M1A", "OPEN_AFTER_M1A_M1B"])

    def test_partition_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["m1_common_snapshot_preflight_resolution"]["exports_object_ready"] = 15
        self.assertTrue(checker.check(value))

    def test_gate_hash_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["gate_disposition"]["accepted_common_snapshot_hashes"] = 2
        self.assertTrue(checker.check(value))

    def test_downstream_promotions_fail(self):
        for flag in (
            "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE", "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE",
            "M1C_COMMON_MANIFEST_REPLAY_COMPLETE", "M1_COMMON_STRICT_SNAPSHOT_COMPLETE",
            "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX", "CLASSICAL_IMPORT_GATE_PASSED",
            "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
