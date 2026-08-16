from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v48.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v48.py"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V48.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v48.md"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v48.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "lorentzian_weyl_bv_completion_atlas_v48_source")
checker = load(CHECKER, "lorentzian_weyl_bv_completion_atlas_v48_checker")


class LorentzianWeylBVCompletionAtlasV48Tests(unittest.TestCase):
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

    def test_classical_routes_retired_and_quantum_frontier_explicit(self):
        routes = [row["route"] for row in self.value["route_selection"]]
        self.assertEqual(routes[:3], [
            "STRICT_Q2_Q3_TYPED_GREEN_COMPATIBILITY",
            "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
            "STRICT_BRST_HADAMARD_TWO_POINT_OR_OBSTRUCTION",
        ])
        self.assertFalse({"STRICT_M1B_ACTION_DUAL_LIFT", "STRICT_M1B_TYPED_CYCLIC_REPLAY", "STRICT_M1C_COMMON_MANIFEST_REPLAY"}.intersection(routes))

    def test_snapshot_mutations_fail(self):
        for path, key, replacement in (
            ("strict_m1b_action_dual_lift", "identity_defects", 1),
            ("strict_m1b_typed_cyclic_composite", "verification_core_is_authoritative_full_bv_source", True),
            ("strict_m1c_common_snapshot", "exports_bound", 19),
            ("classical_import_reconciliation", "snapshot_sha256", "0" * 64),
        ):
            with self.subTest(path=path, key=key):
                value = copy.deepcopy(self.value)
                value[path][key] = replacement
                self.assertTrue(checker.check(value))

    def test_quantum_promotions_fail(self):
        for flag in (
            "strict_386_q2_q3_green_compatibility_certified", "strict_386_full_bv_hadamard_state_constructed",
            "renormalized_lorentzian_products_constructed", "strict_pure_weyl_qme_restored",
            "residual_quantum_transfer_authorized", "lorentzian_full_theory_certified",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))

    def test_stale_pre_freeze_nonclaim_fails(self):
        value = copy.deepcopy(self.value)
        value["does_not_establish"].append("a passed strict pure-Weyl classical import gate")
        self.assertIn("stale pre-V48 nonclaim", checker.check(value))


if __name__ == "__main__":
    unittest.main()
