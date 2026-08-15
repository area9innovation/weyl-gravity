from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "foundations"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_lorentzian_weyl_bv_completion_atlas_v5.py", "test_atlas_v5_builder")
checker = module(HERE / "check_lorentzian_weyl_bv_completion_atlas_v5.py", "test_atlas_v5_checker")
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5.json"
REPORT = HERE / "reports/lorentzian-weyl-bv-completion-atlas-v5.md"


class LorentzianWeylBVCompletionAtlasV5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(checker.check(self.value)[0], [])

    def test_generated_artifacts_current(self):
        result, report = builder.generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_coefficient_count_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["strict_endpoint_q1_content_bridge"]["bach_columns_matching"] = 699
        self.assertTrue(checker.check(value)[0])

    def test_pairing_sign_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["strict_endpoint_q1_content_bridge"]["transported_ghost_pairing_canonical"] = True
        self.assertTrue(checker.check(value)[0])

    def test_full_pairing_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["strict_full_386_pairing_serialized"] = True
        self.assertTrue(checker.check(value)[0])

    def test_gate_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["strict_pure_weyl_classical_gate_passed"] = True
        self.assertTrue(checker.check(value)[0])

    def test_q2_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["strict_386_q2_green_compatibility_certified"] = True
        self.assertTrue(checker.check(value)[0])

    def test_hadamard_or_qme_promotion_fails(self):
        for key in ("berger_brst_hadamard_state_constructed", "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified"):
            with self.subTest(key=key):
                value = copy.deepcopy(self.value)
                value["claim_flags"][key] = True
                self.assertTrue(checker.check(value)[0])


if __name__ == "__main__":
    unittest.main()
