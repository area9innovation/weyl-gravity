from __future__ import annotations

import importlib.util
from json import loads
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "quantum-weyl/classical_import/verify_strict_dfinite_residual_sdr.py"
spec = importlib.util.spec_from_file_location("strict_dfinite_sdr_verifier", VERIFY)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify = module.verify
checker = module.checker
RESULT = module.RESULT
REPORT = module.REPORT


class StrictDFiniteResidualSDRTests(unittest.TestCase):
    def value(self) -> dict:
        return loads(RESULT.read_text())

    def repin(self, value: dict, block_index: int, matrix_name: str) -> None:
        matrix = value["blocks"][block_index]["matrices"][matrix_name]
        matrix["sha256"] = checker.canonical_hash({key: matrix[key] for key in ("name", "rows", "columns", "entries")})
        value["global_direct_sum"]["differential_hash"] = checker.canonical_hash([
            item["matrices"]["q0"]["sha256"] for item in value["blocks"]
        ])
        value["global_direct_sum"]["residual_sdr_hash"] = checker.canonical_hash([
            [item["matrices"][name]["sha256"] for name in ("iota_cl", "pi_cl", "s_cl", "q_res_0")]
            for item in value["blocks"]
        ])
        value["independent_checker"]["expected_digest"] = checker.digest(value)

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_q0_entry_mutation_fails_after_repin(self):
        value = self.value()
        value["blocks"][0]["matrices"]["q0"]["entries"].pop(0)
        self.repin(value, 0, "q0")
        self.assertTrue(verify(result=value)[0])

    def test_s_cl_entry_mutation_fails_after_repin(self):
        value = self.value()
        value["blocks"][3]["matrices"]["s_cl"]["entries"].pop()
        self.repin(value, 3, "s_cl")
        self.assertTrue(verify(result=value)[0])

    def test_basis_reordering_fails_after_repin(self):
        value = self.value()
        basis = value["blocks"][1]["residual_basis"]
        basis[0], basis[1] = basis[1], basis[0]
        value["blocks"][1]["basis_hashes"]["residual"] = checker.canonical_hash(basis)
        value["global_direct_sum"]["residual_basis_hash"] = checker.canonical_hash([
            label for item in value["blocks"] for label in item["residual_basis"]
        ])
        value["independent_checker"]["expected_digest"] = checker.digest(value)
        self.assertTrue(verify(result=value)[0])

    def test_float_like_coefficient_fails(self):
        value = self.value()
        value["blocks"][0]["matrices"]["q0"]["entries"][0][2] = "0.5"
        self.repin(value, 0, "q0")
        self.assertTrue(verify(result=value)[0])

    def test_gate_a_promotion_fails(self):
        value = self.value()
        value["gate_a_effect"]["gate_a_status"] = "VERIFIED"
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        value["independent_checker"]["expected_digest"] = checker.digest(value)
        self.assertTrue(verify(result=value)[0])

    def test_continuum_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["FULL_SUPPORT_LOCAL_RESIDUAL_SDR_CONSTRUCTED"] = True
        self.assertTrue(verify(result=value)[0])

    def test_provenance_drift_fails(self):
        value = self.value()
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
