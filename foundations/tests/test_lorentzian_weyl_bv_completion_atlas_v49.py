from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v49.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v49.py"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v49.md"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v49.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "lorentzian_weyl_bv_completion_atlas_v49_source")
checker = load(CHECKER, "lorentzian_weyl_bv_completion_atlas_v49_checker")


class LorentzianWeylBVCompletionAtlasV49Tests(unittest.TestCase):
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

    def test_77_cells_preserved(self):
        self.assertEqual(len(self.value["branches"]), 7)
        self.assertEqual(sum(len(branch["stages"]) for branch in self.value["branches"]), 77)

    def test_hadamard_bridge_is_closed_but_state_is_not_promoted(self):
        flags = self.value["claim_flags"]
        self.assertTrue(flags["strict_386_q2_q3_green_compatibility_certified"])
        self.assertTrue(flags["strict_386_full_bv_hadamard_two_point_constructed"])
        self.assertTrue(flags["strict_386_full_bv_brst_ward_certified"])
        self.assertFalse(flags["strict_386_full_bv_hadamard_state_constructed"])
        self.assertFalse(flags["strict_386_physical_cohomology_positivity_certified"])

    def test_closed_routes_are_retired(self):
        routes = [row["route"] for row in self.value["route_selection"]]
        self.assertEqual(routes[:3], [
            "STRICT_PHYSICAL_COHOMOLOGY_POSITIVITY_DECISION",
            "STRICT_LORENTZIAN_RENORMALIZED_TIME_ORDERED_PRODUCTS",
            "STRICT_LOCAL_ANOMALY_CLASSIFICATION_AND_QME_RESTORATION",
        ])
        self.assertNotIn("STRICT_Q2_Q3_TYPED_GREEN_COMPATIBILITY", routes)
        self.assertNotIn("STRICT_BRST_HADAMARD_TWO_POINT_OR_OBSTRUCTION", routes)

    def test_projection_mutations_fail(self):
        for path, key, replacement in (
            ("strict_m2_q2_q3_typed_green_compatibility", "exact_or_structural_defects", 1),
            ("strict_m2_q2_q3_typed_green_compatibility", "infinite_tree_series_convergence", True),
            ("strict_386_brst_hadamard_two_point", "proof_obligations", 10),
            ("strict_386_brst_hadamard_two_point", "positive_state_constructed", True),
        ):
            with self.subTest(path=path, key=key):
                value = copy.deepcopy(self.value)
                value[path][key] = replacement
                self.assertTrue(checker.check(value))

    def test_downstream_promotions_fail(self):
        for flag in (
            "strict_386_full_bv_hadamard_state_constructed",
            "strict_386_physical_cohomology_positivity_certified",
            "renormalized_lorentzian_products_constructed",
            "strict_pure_weyl_qme_restored",
            "residual_quantum_transfer_authorized",
            "lorentzian_full_theory_certified",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
