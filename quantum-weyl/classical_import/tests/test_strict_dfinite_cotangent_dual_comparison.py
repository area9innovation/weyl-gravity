from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_strict_dfinite_cotangent_dual_comparison.py"
CHECKER = HERE / "check_strict_dfinite_cotangent_dual_comparison.py"
RESULT = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
REPORT = HERE / "REPORT_STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.md"
SCHEMA = HERE / "schema/strict-dfinite-cotangent-dual-comparison-v1.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "strict_dfinite_cotangent_dual_comparison_source")
checker = load(CHECKER, "strict_dfinite_cotangent_dual_comparison_checker")


class StrictDFiniteCotangentDualComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current_schema_and_independent_replay(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_original_source_has_no_dual_cohomology(self):
        blocks = self.value["original_source_cohomology"]["blocks"]
        self.assertEqual(
            [block["cohomology_dimensions_by_degree"]["0"] for block in blocks],
            [10, 40, 82, 136, 202],
        )
        self.assertEqual(
            [block["cohomology_dimensions_by_degree"]["1"] for block in blocks],
            [0, 0, 0, 0, 0],
        )
        self.assertFalse(
            self.value["same_source_impossibility"]["same_source_deformation_retract_to_940_possible"]
        )

    def test_formal_cotangent_comparison_is_exact(self):
        formal = self.value["formal_cotangent_completion"]
        self.assertEqual((formal["full_dimension"], formal["residual_dimension"]), (8980, 940))
        self.assertEqual((formal["full_pairing_rank"], formal["residual_pairing_rank"]), (8980, 940))
        self.assertTrue(all(
            not any(block["exact_identity_replay"].values())
            for block in formal["block_comparisons"]
        ))

    def test_dual_map_hash_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["formal_cotangent_completion"]["block_comparisons"][0]["dual_maps"]["q_dual"]["entries_sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_same_source_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["same_source_impossibility"]["same_source_deformation_retract_to_940_possible"] = True
        self.assertTrue(checker.check(value))

    def test_action_identification_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["action_support_identification"]["status"] = "COMPLETE"
        value["claim_flags"]["FORMAL_DUAL_IDENTIFIED_WITH_ACTION_SUPPORT_DUAL"] = True
        value["claim_flags"]["M3RC_ACTION_SUPPORT_IDENTIFICATION_COMPLETE"] = True
        self.assertTrue(checker.check(value))

    def test_quantum_promotions_fail(self):
        for flag in (
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
            "CLASSICAL_IMPORT_GATE_PASSED",
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
            "QME_RESTORED",
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
