from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_386_diff_auxiliary_bv_representation_v2.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_386_diff_auxiliary_bv_representation_v2.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Strict386DiffAuxiliaryBVRepresentationV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load(BUILDER, "strict_386_diff_aux_v2_builder")
        cls.checker = load(CHECKER, "strict_386_diff_aux_v2_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.builder.generated()[0], RESULT.read_bytes())

    def test_independent_replay(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_append_only_repair_closes_identity(self):
        repair = self.value["canonical_sign_repair"]
        self.assertEqual(repair["unrepaired_q1_q2_nonzero_coefficients"], 336)
        self.assertEqual(repair["repaired_q1_q2_nonzero_coefficients"], 0)
        self.assertEqual(self.value["repair_of"], "STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1")

    def test_common_union_remains_open(self):
        self.assertFalse(self.value["claim_flags"]["FULL_SOURCE_Q2_COMMON_UNION_ASSEMBLED"])
        self.assertFalse(self.value["claim_flags"]["FULL_SOURCE_Q3_PULLBACK_REPLAYED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["BV_representation_lifts"][0]["c_star_output_entries"][0]["coefficient"] = "31"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
