from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v45.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v45.py"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V45.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v45.md"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v45.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "lorentzian_weyl_bv_completion_atlas_v45_source")
checker = load(CHECKER, "lorentzian_weyl_bv_completion_atlas_v45_checker")


class LorentzianWeylBVCompletionAtlasV45Tests(unittest.TestCase):
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

    def test_m1_routes_reflect_completed_local_stage(self):
        self.assertEqual([row["route"] for row in self.value["route_selection"][:4]], [
            "STRICT_M1A3_REPRESENTED_CROSSWALK",
            "STRICT_M1A4_LEDGER_FREEZE",
            "STRICT_M1B_REPRESENTED_COMPOSITE_CONTRACTION",
            "STRICT_M1C_COMMON_MANIFEST_REPLAY",
        ])

    def test_local_semantic_mutations_fail(self):
        for key, replacement in (
            ("local_386_rows_fully_namespaced", 385),
            ("scalar_nonlinear_weyl_weight", "UNKNOWN"),
            ("cotton_component_defects", 1),
        ):
            with self.subTest(key=key):
                value = copy.deepcopy(self.value)
                value["strict_m1a_local_semantic_extension"][key] = replacement
                self.assertTrue(checker.check(value))

    def test_promotions_fail(self):
        for flag in (
            "strict_M1A3_represented_crosswalk_complete", "strict_M1A4_ledger_freeze_complete",
            "strict_M1A_full_typed_carrier_ledger_complete", "strict_M1B_represented_composite_contraction_complete",
            "strict_M1C_common_manifest_replay_complete", "strict_M1_common_strict_snapshot_complete",
            "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed",
            "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
