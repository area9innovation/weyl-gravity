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
RESULT = HERE / "certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("strict_cylinder_bach_universal_check", HERE / "check_strict_cylinder_bach_universal_export.py")
VERIFY = module("strict_cylinder_bach_universal_verify", HERE / "verify_strict_cylinder_bach_universal_export.py")


class StrictCylinderBachUniversalExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.md").read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_fast_checker_cli(self) -> None:
        result = subprocess.run([sys.executable, str(HERE / "check_strict_cylinder_bach_universal_export.py")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_basis_factorial_convention_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["universal_table"]["input_basis"][1]["word"] = [0, 0, 0, 2]
        self.assertTrue(any("basis drift" in error for error in CHECK.check(value)))

    def test_coefficient_dictionary_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["universal_table"]["coefficient_dictionary"][0] = "0"
        self.assertTrue(any("coefficient dictionary" in error for error in CHECK.check(value)))

    def test_noncanonical_bilinear_entry_fails(self) -> None:
        value = copy.deepcopy(self.value)
        entry = value["universal_table"]["rows"][0]["symmetric_bilinear_entries"][0]
        entry[0], entry[1] = entry[1], entry[0]
        self.assertTrue(any("canonical bilinear" in error for error in CHECK.check(value)))

    def test_table_count_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["universal_table"]["counts"]["symmetric_bilinear_terms"] -= 1
        self.assertTrue(any("counts" in error for error in CHECK.check(value)))

    def test_point_crosscheck_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["exact_checks"]["three_independent_point_evaluator_crosschecks"][0]["output"][0] = "0"
        self.assertTrue(any("crosscheck failed" in error for error in CHECK.check(value)))

    def test_implementation_hash_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["implementation"]["universal_engine"]["sha256"] = "0" * 64
        self.assertTrue(any("implementation drift" in error for error in CHECK.check(value)))

    def test_open_gate_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["next_gates"][0]["status"] = "PASS"
        self.assertTrue(any("next-gate" in error for error in CHECK.check(value)))

    def test_globalization_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["PORTABLE_TENSOR_NATURAL_HSTAR_ROW"] = True
        self.assertTrue(any("claim boundary" in error for error in CHECK.check(value)))

    def test_receiver_declaration_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["independent_receiver"]["cost_class"] = "TIER_2_EXHAUSTIVE"
        self.assertTrue(any("receiver declaration" in error for error in CHECK.check(value)))

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("TENSOR_NATURAL_GLOBALIZATION", "GLOBALIZATION")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
