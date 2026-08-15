from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v29.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v29.py"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V29.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class LorentzianWeylCompletionAtlasV29Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "atlas_v29_source")
        cls.checker = load(CHECKER, "atlas_v29_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_checker(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_frontier_contracted(self):
        routes = [item["route"] for item in self.value["route_selection"]]
        self.assertEqual(routes[:3], ["STRICT_DIFF_AUXILIARY_BV_REPRESENTATION_COMPONENTS", "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST", "STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY"])
        self.assertNotIn("STRICT_SECOND_FRECHET_HH_HV_AUXILIARY_SHIFT_COMPONENTS", routes)

    def test_fail_closed(self):
        flags = self.value["claim_flags"]
        self.assertTrue(flags["strict_386_full_quadratic_bv_cotangent_lift_serialized"])
        self.assertFalse(flags["strict_386_full_source_q2_pullback_replayed"])
        self.assertFalse(flags["strict_pure_weyl_classical_gate_passed"])
        self.assertFalse(flags["strict_386_full_bv_hadamard_state_constructed"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["route_selection"][0]["route"] = "WRONG"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
