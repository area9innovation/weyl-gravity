from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v42.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v42.py"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V42.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v42.md"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v42.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "lorentzian_weyl_bv_completion_atlas_v42_source")
checker = load(CHECKER, "lorentzian_weyl_bv_completion_atlas_v42_checker")


class LorentzianWeylBVCompletionAtlasV42Tests(unittest.TestCase):
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

    def test_m4r_is_first_route(self):
        self.assertEqual(len(self.value["route_selection"]), 8)
        self.assertEqual(self.value["route_selection"][0]["route"], "STRICT_TYPED_RESIDUAL_CYCLICITY")
        self.assertEqual(self.value["route_selection"][1]["route"], "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION")

    def test_action_dual_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["strict_m3rc_action_support_dual_identification"]["action_pairing_rank"] = 939
        self.assertTrue(checker.check(value))

    def test_promotions_fail(self):
        for flag in (
            "strict_M4R_typed_residual_cyclicity_complete",
            "strict_full_all_energy_continuous_dual_identified",
            "strict_formal_8980_source_is_authoritative_original_BV_complex",
            "strict_pure_weyl_classical_gate_passed",
            "strict_386_full_bv_hadamard_state_constructed",
            "strict_pure_weyl_qme_restored",
            "lorentzian_full_theory_certified",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
