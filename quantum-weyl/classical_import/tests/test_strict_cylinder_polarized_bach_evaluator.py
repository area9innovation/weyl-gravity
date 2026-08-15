from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
RESULT = HERE / "certificates/STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("strict_cylinder_bach_evaluator_check", HERE / "check_strict_cylinder_polarized_bach_evaluator.py")
VERIFY = module("strict_cylinder_bach_evaluator_verify", HERE / "verify_strict_cylinder_polarized_bach_evaluator.py")


class StrictCylinderPolarizedBachEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1.md").read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_artifacts_are_current(self) -> None:
        result = subprocess.run([sys.executable, str(HERE / "build_strict_cylinder_polarized_bach_evaluator.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_sparse_coefficient_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["arbitrary_sparse_trial"]["output"][0]["coefficient"] = "-5"
        self.assertTrue(any("sparse-trial output" in error for error in CHECK.check(value)))

    def test_trace_identity_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["arbitrary_sparse_trial"]["trace_identity_defect"] = "1"
        self.assertTrue(any("Weyl trace" in error for error in CHECK.check(value)))

    def test_ppwave_promotion_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["ppwave_restriction_trials"][0]["all_ten_outputs_zero"] = False
        self.assertTrue(any("pp-wave" in error for error in CHECK.check(value)))

    def test_stage_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["benchmark_stage_progress"][-1]["status"] = "PROTOTYPE_EXECUTED"
        self.assertTrue(any("stage progress" in error for error in CHECK.check(value)))

    def test_diff_open_gate_removal_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["open_acceptance_gates"] = [item for item in value["open_acceptance_gates"] if "Diff Noether" not in item]
        self.assertTrue(any("open acceptance" in error for error in CHECK.check(value)))

    def test_universal_ast_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["GENERAL_UNIVERSAL_COMPONENT_AST_EXPORTED"] = True
        self.assertTrue(any("claim boundary" in error for error in CHECK.check(value)))

    def test_action_normalization_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["scope"]["action_normalization"] = "B_action=B_standard"
        self.assertTrue(any("normalization" in error for error in CHECK.check(value)))

    def test_implementation_hash_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["implementation"]["sha256"] = "0" * 64
        self.assertTrue(any("implementation hash" in error for error in CHECK.check(value)))

    def test_exact_check_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["exact_checks"]["three_ppwave_polynomial_trials_zero"] = False
        self.assertTrue(any("exact check" in error for error in CHECK.check(value)))

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("not yet the universal component AST", "a component evaluator")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
