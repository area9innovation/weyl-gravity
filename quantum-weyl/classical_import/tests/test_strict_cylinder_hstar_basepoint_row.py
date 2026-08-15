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
RESULT = HERE / "certificates/STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("strict_cylinder_hstar_basepoint_check", HERE / "check_strict_cylinder_hstar_basepoint_row.py")
VERIFY = module("strict_cylinder_hstar_basepoint_verify", HERE / "verify_strict_cylinder_hstar_basepoint_row.py")


class StrictCylinderHstarBasepointRowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.md").read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_fast_checker_cli(self) -> None:
        result = subprocess.run([sys.executable, str(HERE / "check_strict_cylinder_hstar_basepoint_row.py")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_source_sign_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["source_crosswalk"]["authoritative_Q_g_star_terms"][0]["coefficient"] = 2
        self.assertTrue(CHECK.check(value))

    def test_diagonal_half_factor_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["universal_table_reference"]["diagonal_Taylor_multiplier"] = "1"
        self.assertTrue(any("factor" in error or "reference" in error for error in CHECK.check(value)))

    def test_diff_density_term_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["components"][1]["coordinate_formula"] = value["components"][1]["coordinate_formula"].replace(" + (partial_rho c^rho) h_star^{mu nu}", "")
        self.assertTrue(any("formula" in error for error in CHECK.check(value)))

    def test_weyl_sign_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["components"][2]["coefficient"] = "1"
        self.assertTrue(any("formula" in error or "inventory" in error for error in CHECK.check(value)))

    def test_universal_table_hash_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["universal_table_reference"]["universal_table_sha256"] = "0" * 64
        self.assertTrue(any("reference" in error for error in CHECK.check(value)))

    def test_open_gate_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["gates"][1]["status"] = "PASS"
        self.assertTrue(any("gate ledger" in error for error in CHECK.check(value)))

    def test_portability_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["PORTABLE_TENSOR_NATURAL_HSTAR_ROW"] = True
        self.assertTrue(any("claim boundary" in error for error in CHECK.check(value)))

    def test_missing_object_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["missing_object_ledger"][0]["status"] = "AVAILABLE"
        self.assertTrue(any("missing-object" in error for error in CHECK.check(value)))

    def test_exact_replay_hash_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["exact_checks"]["three_diff_and_weyl_variational_cotangent_checks"][0]["diff_output_sha256"] = "0" * 64
        self.assertTrue(any("canonical hashes" in error for error in CHECK.check(value)))

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("SUSPENDED_GRADED_POLARIZATION", "POLARIZATION")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
