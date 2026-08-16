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
SOURCE = HERE / "build_strict_endpoint_to_residual_spectral_comparison.py"
CHECKER = HERE / "check_strict_endpoint_to_residual_spectral_comparison.py"
RESULT = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
REPORT = HERE / "REPORT_STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.md"
SCHEMA = HERE / "schema/strict-endpoint-to-residual-spectral-comparison-v1.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "strict_endpoint_to_residual_spectral_comparison_source")
checker = load(CHECKER, "strict_endpoint_to_residual_spectral_comparison_checker")


class StrictEndpointToResidualSpectralComparisonTests(unittest.TestCase):
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

    def test_exact_470_mode_dictionary(self):
        self.assertEqual([item["dimension"] for item in self.value["level_blocks"]], [10, 40, 82, 136, 202])
        self.assertEqual(len(self.value["ordered_residual_basis"]), 470)
        self.assertEqual(
            len({item["represented_residual_label"] for item in self.value["ordered_residual_basis"]}),
            470,
        )
        self.assertTrue(all(item["unnormalized_lowering_norm_squared"] > 0 for item in self.value["ordered_residual_basis"]))

    def test_crosswalk_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["ordered_residual_basis"][0]["dfinite_residual_label"] = "E2:W_MINUS:0"
        self.assertTrue(checker.check(value))

    def test_lowering_normalization_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["ordered_residual_basis"][-1]["unnormalized_lowering_norm_squared"] += 1
        self.assertTrue(checker.check(value))

    def test_locality_and_completion_promotions_fail(self):
        for flag in (
            "HARMONIC_ANALYSIS_SUPPORT_LOCAL",
            "RAW_ALL_MAGNETIC_COORDINATE_MATRICES_SERIALIZED",
            "ALL_ENERGY_OR_SMOOTH_COMPLETION_CERTIFIED",
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
            "CLASSICAL_IMPORT_GATE_PASSED",
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
            "QME_RESTORED",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))

    def test_zero_mode_overlap_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["support_and_zero_mode_policy"]["excluded_energies"] = [1]
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
