from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_nonaxisymmetric_L3_matrix import fast_check


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L3_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L3_matrix.schema.json"


class NonaxisymmetricL3MatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_schema(self) -> None:
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(self.value)

    def test_complete_workload(self) -> None:
        self.assertEqual(self.value["matrix_summary"]["candidate_rows"], 6)
        self.assertEqual(self.value["matrix_summary"]["ordered_input_basis_fixtures"], 36)
        self.assertEqual(self.value["matrix_summary"]["target_adjoint_coefficients"], 44)

    def test_all_coefficients_are_nonzero(self) -> None:
        self.assertEqual(self.value["matrix_summary"]["zero_target_adjoint_coefficients"], 0)
        self.assertEqual(self.value["matrix_summary"]["nonzero_target_adjoint_coefficients"], 44)

    def test_all_basis_fixtures_are_obstructed(self) -> None:
        self.assertTrue(self.value["classification"]["all_basis_fixtures_bounded_obstructed"])
        self.assertEqual(self.value["matrix_summary"]["basis_fixtures_with_nonzero_cokernel_vector"], 36)

    def test_claim_stays_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["arbitrary_amplitude_zero_variety_classified"])
        self.assertEqual(self.value["classification"]["remaining_nonaxisymmetric_L1_coefficients"], 12)
        self.assertFalse(self.value["classification"]["causal_or_quantum_claim"])

    def test_fast_check(self) -> None:
        fast_check()


if __name__ == "__main__":
    unittest.main()
