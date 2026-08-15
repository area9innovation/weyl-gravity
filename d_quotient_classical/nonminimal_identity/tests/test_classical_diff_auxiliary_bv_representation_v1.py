from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "d_quotient_classical/nonminimal_identity/classical_diff_auxiliary_bv_representation_v1.py"
CHECKER = ROOT / "d_quotient_classical/nonminimal_identity/check_classical_diff_auxiliary_bv_representation_v1.py"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ClassicalDiffAuxiliaryRepresentationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load(SOURCE, "classical_diff_aux_source")
        cls.checker = load(CHECKER, "classical_diff_aux_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.source.generated()[0], RESULT.read_bytes())

    def test_independent_component_replay(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_exact_counts(self):
        self.assertEqual(self.value["component_summary"]["ordered_field_coefficients"], 168)
        self.assertEqual([item["nonzero_ordered_field_coefficients"] for item in self.value["representation_tables"]], [104, 32, 32])

    def test_receiver_boundary_is_fail_closed(self):
        flags = self.value["claim_flags"]
        self.assertFalse(flags["THREE_DIFF_AUXILIARY_BV_COTANGENT_LIFTS_SERIALIZED"])
        self.assertFalse(flags["CLASSICAL_IMPORT_GATE_PASSED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["representation_tables"][0]["ordered_field_action_entries"][0]["coefficient"] = "17"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
