from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v37.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v37.py"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v37.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "lorentzian_weyl_bv_completion_atlas_v37_source")
checker = load(CHECKER, "lorentzian_weyl_bv_completion_atlas_v37_checker")


class LorentzianWeylBvCompletionAtlasV37Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current(self):
        result, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), result)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_independent_replay(self):
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_m3l_route_completed(self):
        routes = [row["route"] for row in self.value["route_selection"]]
        self.assertNotIn("STRICT_COMMON_ENDPOINT_SDR_BINDING", routes)
        self.assertEqual(routes[0], "STRICT_FULL_CYCLIC_PAIRING")
        self.assertTrue(self.value["claim_flags"]["strict_M3L_common_endpoint_sdr_bound"])

    def test_false_residual_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["strict_common_endpoint_sdr_binding"]["residual_comparison_included"] = True
        self.assertTrue(checker.check(value))

    def test_false_gate_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["strict_pure_weyl_classical_gate_passed"] = True
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
