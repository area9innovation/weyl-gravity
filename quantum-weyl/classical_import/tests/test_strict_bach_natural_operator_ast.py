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
RESULT = HERE / "certificates/STRICT_BACH_NATURAL_OPERATOR_AST_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("strict_bach_natural_operator_ast_check", HERE / "check_strict_bach_natural_operator_ast.py")
VERIFY = module("strict_bach_natural_operator_ast_verify", HERE / "verify_strict_bach_natural_operator_ast.py")
AST = module("strict_bach_natural_operator_ast_semantics", HERE / "bach_natural_operator_ast.py")


class StrictBachNaturalOperatorAstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_STRICT_BACH_NATURAL_OPERATOR_AST_V1.md").read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_artifacts_are_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HERE / "build_strict_bach_natural_operator_ast.py"), "--check"],
            cwd=ROOT,
            env={**__import__("os").environ, "PYTHONPATH": str(HERE)},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ast_coefficient_mutation_fails_closed(self) -> None:
        value = copy.deepcopy(self.value)
        value["natural_operator_ast"]["nodes"][-2]["parameters"]["coefficient"] = -1
        self.assertTrue(any("natural AST" in error for error in CHECK.check(value)))

    def test_ast_order_mutation_fails_closed(self) -> None:
        value = copy.deepcopy(self.value)
        value["natural_operator_ast"]["nodes"][5]["declared_metric_jet_order"] = 3
        self.assertTrue(any("natural AST" in error for error in CHECK.check(value)))

    def test_float_is_rejected(self) -> None:
        value = copy.deepcopy(self.value)
        value["natural_operator_ast"]["nodes"][-2]["parameters"]["coefficient"] = -2.0
        self.assertTrue(any("floating-point" in error for error in VERIFY.verify(value, self.report)))

    def test_coordinate_witness_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["exact_evaluator_checks"]["signed_coordinate_permutation"]["exact_covariance"] = False
        self.assertTrue(any("coordinate covariance" in error for error in CHECK.check(value)))

    def test_nariai_adapter_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["cross_background_evidence"]["Nariai_action_Hessian"]["relationship"] = "component adapter certified"
        self.assertTrue(any("Nariai" in error for error in CHECK.check(value)))

    def test_hstar_and_lorentzian_promotions_fail(self) -> None:
        for flag in ("PORTABLE_TENSOR_NATURAL_HSTAR_ROW", "LORENTZIAN_CAUSAL_CERTIFIED"):
            value = copy.deepcopy(self.value)
            value["claim_flags"][flag] = True
            self.assertTrue(any("claim flags" in error for error in CHECK.check(value)))

    def test_open_gate_removal_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["gate_advancement"] = value["gate_advancement"][:1]
        self.assertTrue(any("gate advancement" in error for error in CHECK.check(value)))

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("does **not** claim a direct component adapter", "claims an adapter")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))

    def test_direct_ast_rejects_unknown_node(self) -> None:
        ast = copy.deepcopy(self.value["natural_operator_ast"])
        ast["nodes"][4]["operation"] = "coordinate_fit"
        with self.assertRaisesRegex(AST.NaturalOperatorAstError, "canonical"):
            AST.validate_ast(ast)


if __name__ == "__main__":
    unittest.main()
