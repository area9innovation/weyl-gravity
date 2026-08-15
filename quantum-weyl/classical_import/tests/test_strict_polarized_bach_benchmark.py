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
RESULT = HERE / "certificates/STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("strict_bach_benchmark_check", HERE / "check_strict_polarized_bach_benchmark.py")
VERIFY = module("strict_bach_benchmark_verify", HERE / "verify_strict_polarized_bach_benchmark.py")


class StrictPolarizedBachBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.md").read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated_artifacts_are_current(self) -> None:
        result = subprocess.run([sys.executable, str(HERE / "build_strict_polarized_bach_benchmark.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_action_normalization_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["target_contract"]["action_normalization"] = "B_action=B_standard"
        self.assertTrue(any("normalization" in error for error in CHECK.check(value)))

    def test_output_type_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["target_contract"]["output"]["tensor_type"]["symmetry"] = "symmetric_covariant_2"
        self.assertTrue(any("output type" in error for error in CHECK.check(value)))

    def test_bach_formula_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        step = next(item for item in value["candidate_program_contract"] if item["operation"] == "bach_standard")
        step["output"] = "B_standard_ab=Box Ric_ab"
        self.assertTrue(any("Bach formula" in error for error in CHECK.check(value)))

    def test_nonzero_channel_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        fixture = next(item for item in value["fixture_ledger"] if item["fixture_id"] == "CYLINDER_HT1B_NONZERO_MODE_CHANNELS")
        fixture["expected"]["channels"][0]["integrated_taub_charge"] = "Integer(0)"
        self.assertTrue(any("nonzero cylinder" in error for error in CHECK.check(value)))

    def test_ppwave_zero_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        fixture = next(item for item in value["fixture_ledger"] if item["fixture_id"] == "PPWAVE_ARBITRARY_PROFILE_ZERO_SLICE")
        fixture["expected"]["q2_entries"]["Einstein_extraWeyl"] = "1"
        self.assertTrue(any("pp-wave" in error for error in CHECK.check(value)))

    def test_nariai_rank_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        fixture = next(item for item in value["fixture_ledger"] if item["fixture_id"] == "NARIAI_TRANSVERSE_HESSIAN_VARIATION")
        fixture["expected"]["coefficient_map_rank"] = 44
        self.assertTrue(any("Nariai" in error for error in CHECK.check(value)))

    def test_gate_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["acceptance_gates"][0]["status"] = "PASS"
        self.assertTrue(any("promoted" in error for error in CHECK.check(value)))

    def test_general_kernel_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["GENERAL_ARBITRARY_INPUT_CYLINDER_BACH_KERNEL_AVAILABLE"] = True
        self.assertTrue(any("claim boundary" in error for error in CHECK.check(value)))

    def test_coverage_gap_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["coverage_diagnosis"]["general_arbitrary_input_cylinder_tensor_available"] = True
        self.assertTrue(any("coverage gap" in error for error in CHECK.check(value)))

    def test_provenance_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(any("provenance drift" in error for error in CHECK.check(value)))

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("two unary cross terms", "cross terms")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
