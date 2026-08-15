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
RESULT = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("strict_portable_local_q1_check", HERE / "check_strict_portable_local_q1_ast.py")
VERIFY = module("strict_portable_local_q1_verify", HERE / "verify_strict_portable_local_q1_ast.py")
Q1 = module("strict_portable_local_q1_semantics", HERE / "local_q1_bach_flat.py")


class StrictPortableLocalQ1AstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_STRICT_PORTABLE_LOCAL_Q1_AST_V1.md").read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_artifacts_are_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HERE / "build_strict_portable_local_q1_ast.py"), "--check"],
            cwd=ROOT,
            env={**__import__("os").environ, "PYTHONPATH": str(HERE)},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ast_mutation_fails_closed(self) -> None:
        value = copy.deepcopy(self.value)
        value["local_q1_ast"]["nodes"][3]["parameters"]["parent_node"] = "K_hh"
        self.assertTrue(any("AST rejected" in error for error in CHECK.check(value)))

    def test_bach_flat_hypothesis_removal_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["scope"]["background_equation"] = "none"
        self.assertTrue(any("Bach-flat" in error for error in CHECK.check(value)))

    def test_fixture_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["square_zero_theorem"]["exact_fixture_records"][0]["checks"]["B_linear_after_R_diff_zero"] = False
        self.assertTrue(any("fixture drift" in error for error in CHECK.check(value)))

    def test_arity_two_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED"] = True
        self.assertTrue(any("claim flags" in error for error in CHECK.check(value)))

    def test_direct_ast_rejects_non_degree_one_component(self) -> None:
        ast = copy.deepcopy(self.value["local_q1_ast"])
        ast["components"][0]["output"] = "c_star"
        with self.assertRaises(Q1.LocalQ1Error):
            Q1.validate_ast(ast)

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("does not silently claim an off-shell background", "is off shell")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
