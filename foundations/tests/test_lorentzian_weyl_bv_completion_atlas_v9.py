from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "foundations"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_lorentzian_weyl_bv_completion_atlas_v9.py", "test_atlas_v9_builder")
checker = module(HERE / "check_lorentzian_weyl_bv_completion_atlas_v9.py", "test_atlas_v9_checker")
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9.json"
REPORT = HERE / "reports/lorentzian-weyl-bv-completion-atlas-v9.md"


class CompletionAtlasV9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(checker.check(self.value), [])

    def test_generated_current(self):
        result, report = builder.generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_sign_discriminator_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["strict_full_q1_split_sign_gate"]["declared_cyclicity_defects"] = 0
        self.assertTrue(checker.check(value))

    def test_repair_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["strict_full_q1_split_sign_gate"]["repair_applied"] = True
        self.assertTrue(checker.check(value))

    def test_full_q1_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["strict_full_386_q1_portable_component_bytes"] = True
        self.assertTrue(checker.check(value))

    def test_causal_theorem_revocation_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["strict_causal_green_homotopy_theorem_preserved"] = False
        self.assertTrue(checker.check(value))

    def test_route_order_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["route_selection"][0], value["route_selection"][1] = value["route_selection"][1], value["route_selection"][0]
        self.assertTrue(checker.check(value))

    def test_quantum_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["lorentzian_full_theory_certified"] = True
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
