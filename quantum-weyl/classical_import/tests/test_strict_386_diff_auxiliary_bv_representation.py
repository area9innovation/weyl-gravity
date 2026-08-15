from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_386_diff_auxiliary_bv_representation.py"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_386_diff_auxiliary_bv_representation.py"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Strict386DiffAuxiliaryBVRepresentationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load(BUILDER, "strict_386_diff_aux_builder")
        cls.checker = load(CHECKER, "strict_386_diff_aux_checker")
        cls.value = json.loads(RESULT.read_text())

    def test_generated_current(self):
        self.assertEqual(self.builder.generated()[0], RESULT.read_bytes())

    def test_independent_variational_replay(self):
        self.assertEqual(self.checker.check(self.value), [])

    def test_exact_counts(self):
        self.assertEqual(self.value["component_summary"], {
            "carrier_rows": 386, "completed_families": 3,
            "master_density_coefficients": 264, "field_output_coefficients": 336,
            "antifield_output_coefficients": 632, "c_star_output_coefficients": 704,
            "formal_variational_defects": 0, "Koszul_symmetry_defects": 0,
        })

    def test_known_complete_is_not_exhaustive(self):
        complete = self.value["inventory_completeness"]
        self.assertEqual(complete["component_coefficient_complete_families"], 7)
        self.assertFalse(complete["exhaustive_full_nonlinear_BV_family_census"])
        self.assertFalse(self.value["claim_flags"]["FULL_Q1_Q2_IDENTITY_REPLAYED"])

    def test_mutation_detected(self):
        changed = json.loads(json.dumps(self.value))
        changed["BV_representation_lifts"][1]["c_star_output_entries"][0]["coefficient"] = "23"
        self.assertTrue(self.checker.check(changed))


if __name__ == "__main__":
    unittest.main()
