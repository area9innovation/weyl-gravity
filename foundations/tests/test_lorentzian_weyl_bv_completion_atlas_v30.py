from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v30.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v30.py"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V30.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class LorentzianWeylBVCompletionAtlasV30Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "atlas_v30_source")
        cls.checker = load(CHECKER, "atlas_v30_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_checker(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_routes_contract(self):
        self.assertEqual(len(self.value["route_selection"]), 11)
        self.assertEqual(self.value["route_selection"][0]["route"], "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST")

    def test_known_complete_not_exhaustive(self):
        result = self.value["strict_diff_auxiliary_bv_representation"]
        self.assertEqual((result["known_required_cubic_families"], result["component_complete_families"], result["component_open_families"]), (7, 7, 0))
        self.assertFalse(result["exhaustive_full_nonlinear_BV_family_census"])
        self.assertFalse(self.value["claim_flags"]["strict_pure_weyl_classical_gate_passed"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["strict_diff_auxiliary_bv_representation"]["component_complete_families"] = 6
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
