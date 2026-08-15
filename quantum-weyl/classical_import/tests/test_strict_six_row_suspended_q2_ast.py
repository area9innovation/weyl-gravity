from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
RESULT = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("strict_six_row_suspended_q2_check", HERE / "check_strict_six_row_suspended_q2_ast.py")
VERIFY = module("strict_six_row_suspended_q2_verify", HERE / "verify_strict_six_row_suspended_q2_ast.py")


class StrictSixRowSuspendedQ2AstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.md").read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_artifacts_are_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HERE / "build_strict_six_row_suspended_q2_ast.py"), "--check"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(HERE)},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_mixed_koszul_sign_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        row = next(item for item in value["ordered_components"] if item["orientation"] == "KOSZUL_SWAP" and item["koszul_swap_sign"] == -1)
        row["coefficient_relative_to_primary"] *= -1
        self.assertTrue(any("Koszul" in error for error in CHECK.check(value)))

    def test_odd_self_pair_sign_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        row = next(item for item in value["primary_components"] if item["primary_id"] == "q2_c_cc")
        row["intrinsic_swap_sign"] = 1
        self.assertTrue(any("intrinsic" in error for error in CHECK.check(value)))

    def test_bach_root_hash_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        row = next(item for item in value["primary_components"] if item["primary_id"] == "q2_hstar_hh")
        row["portable_semantics"]["ast_sha256"] = "0" * 64
        self.assertTrue(any("Bach root" in error for error in CHECK.check(value)))

    def test_row_omission_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["row_completeness"][-1]["ordered_component_ids"] = []
        self.assertTrue(any("row-completeness" in error for error in CHECK.check(value)))

    def test_degree_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["generator_ledger"][1]["local_tangent_degree"] = 0
        self.assertTrue(any("generator" in error for error in CHECK.check(value)))

    def test_identity_promotion_fails(self) -> None:
        for flag in ("Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED", "STRICT_SUPPORT_LOCAL_Q2_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED"):
            value = copy.deepcopy(self.value)
            value["claim_flags"][flag] = True
            self.assertTrue(any("claim flags" in error for error in CHECK.check(value)))

    def test_float_is_rejected(self) -> None:
        value = copy.deepcopy(self.value)
        value["primary_components"][0]["coefficient"] = 1.0
        self.assertTrue(any("floating-point" in error for error in VERIFY.verify(value, self.report)))

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("not yet satisfy", "already satisfies")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
