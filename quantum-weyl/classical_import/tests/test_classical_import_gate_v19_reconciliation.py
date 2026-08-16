from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_classical_import_gate_v19_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v19_reconciliation.py"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V19_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V19.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "classical_import_gate_v19_source")
checker = load(CHECKER, "classical_import_gate_v19_checker")


class ClassicalImportGateV19Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_repository_gate_replays(self):
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])
        self.assertEqual(
            [item["id"] for item in self.value["minimal_missing_bundle"]],
            ["M1_COMMON_STRICT_SNAPSHOT", "M3R_TYPED_RESIDUAL_COMPARISON", "M4_FULL_CYCLIC_PAIRING"],
        )

    def test_m3l_is_scoped_complete(self):
        resolution = self.value["m3l_common_endpoint_sdr_binding_resolution"]
        self.assertEqual(resolution["total_projected_identity_defects"], 0)
        self.assertTrue(self.value["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"])
        self.assertFalse(resolution["residual_comparison_included"])

    def test_false_residual_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"] = True
        self.assertTrue(checker.check(value, replay_binding=False))

    def test_false_gate_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value, replay_binding=False))

    def test_manifest_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["m3l_common_endpoint_sdr_binding_resolution"]["common_manifest_sha256"] = "0" * 64
        self.assertTrue(checker.check(value, replay_binding=False))


if __name__ == "__main__":
    unittest.main()
