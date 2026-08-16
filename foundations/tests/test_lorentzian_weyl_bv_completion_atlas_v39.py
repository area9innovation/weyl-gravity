from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v39.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v39.py"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V39.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v39.md"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v39.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "lorentzian_weyl_bv_completion_atlas_v39_source")
checker = load(CHECKER, "lorentzian_weyl_bv_completion_atlas_v39_checker")


class LorentzianWeylBvCompletionAtlasV39Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current_schema_and_independent_replay(self):
        result, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_m3r_completed_and_m4r_first(self):
        routes = [row["route"] for row in self.value["route_selection"]]
        self.assertNotIn("STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON", routes)
        self.assertEqual("STRICT_TYPED_RESIDUAL_CYCLICITY", routes[0])
        self.assertTrue(self.value["claim_flags"]["strict_M3R_typed_residual_comparison_constructed"])

    def test_false_support_local_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["strict_harmonic_analysis_support_local"] = True
        self.assertTrue(checker.check(value))

    def test_false_residual_cyclicity_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["strict_M4R_typed_residual_cyclicity_complete"] = True
        self.assertTrue(checker.check(value))

    def test_false_gate_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["strict_pure_weyl_classical_gate_passed"] = True
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
