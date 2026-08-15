from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "quantum-weyl/classical_import/build_strict_386_hh_hv_auxiliary_cotangent_lift.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_386_hh_hv_auxiliary_cotangent_lift.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Strict386HhHvCotangentLiftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "strict_hh_hv_source")
        cls.checker = load(CHECKER, "strict_hh_hv_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_euler_adjoint_replay(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_exact_collected_counts(self):
        counts = self.value["quadratic_BV_cotangent_lift"]["cotangent_component_counts_after_collection"]
        self.assertEqual(counts, {"hh_to_h_star": 3411, "hv_to_h_star": 320, "hv_to_v_star": 160, "vv_to_v_star": 16, "combined": 3907})

    def test_quadratic_lift_promoted_only(self):
        flags = self.value["claim_flags"]
        self.assertTrue(flags["FULL_386_QUADRATIC_BV_COTANGENT_LIFT_SERIALIZED"])
        self.assertFalse(flags["DIFF_AUXILIARY_BV_REPRESENTATION_COMPLETE"])
        self.assertFalse(flags["EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS"])
        self.assertFalse(flags["FULL_SOURCE_Q2_PULLBACK_REPLAYED"])
        self.assertFalse(flags["CLASSICAL_IMPORT_GATE_PASSED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["quadratic_BV_cotangent_lift"]["combined_cotangent_entries"][0]["coefficient"] = "0"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
