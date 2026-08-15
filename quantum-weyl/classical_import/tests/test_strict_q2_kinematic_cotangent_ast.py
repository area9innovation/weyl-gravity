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
RESULT = HERE / "certificates/STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("strict_q2_ast_check", HERE / "check_strict_q2_kinematic_cotangent_ast.py")
VERIFY = module("strict_q2_ast_verify", HERE / "verify_strict_q2_kinematic_cotangent_ast.py")


class StrictQ2KinematicCotangentAstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.md").read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_artifacts_are_current(self) -> None:
        result = subprocess.run([sys.executable, str(HERE / "build_strict_q2_kinematic_cotangent_ast.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_coordinate_formula_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["operator_definitions"][0]["coordinate_formula"] = "c^rho partial_rho c^mu"
        self.assertTrue(any("formula drift" in error for error in CHECK.check(value)))

    def test_variational_origin_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["operator_definitions"][0]["variational_origin"]["Euler_variable"] = "omega"
        self.assertTrue(any("variational origin drift" in error for error in CHECK.check(value)))

    def test_exact_coefficient_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        item = next(row for row in value["components"] if row["operator_id"] == "weyl_metric_product")
        item["coefficient"] = 1
        self.assertTrue(any("coefficient drift" in error for error in CHECK.check(value)))

    def test_hard_row_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        row = next(row for row in value["row_ledger"] if row["output"] == "h_star")
        row["status"] = "DIAGONAL_POLYNOMIAL_SERIALIZED"
        self.assertTrue(any("row ledger mismatch" in error for error in CHECK.check(value)))

    def test_polarization_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["SUSPENDED_GRADED_POLARIZATION_REPLAYED"] = True
        self.assertTrue(any("claim boundary" in error for error in CHECK.check(value)))

    def test_interaction_identity_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        gate = next(row for row in value["proof_gates"] if row["check_id"] == "q1_q2_arity_two_nilpotency")
        gate["status"] = "RECEIVER_REPLAYED"
        self.assertTrue(any("premature promotion" in error for error in CHECK.check(value)))

    def test_local_degree_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["generator_ledger"][1]["local_tangent_degree"] = 1
        self.assertTrue(any("grading ledger drift" in error for error in CHECK.check(value)))

    def test_provenance_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(any("provenance drift" in error for error in CHECK.check(value)))

    def test_source_crosswalk_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["source_crosswalk"]["source_Q_rows"]["g"][0][0] = 1
        self.assertTrue(any("serialized source Q" in error for error in CHECK.check(value)))

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("odd ghost diagonal", "ghost diagonal")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
