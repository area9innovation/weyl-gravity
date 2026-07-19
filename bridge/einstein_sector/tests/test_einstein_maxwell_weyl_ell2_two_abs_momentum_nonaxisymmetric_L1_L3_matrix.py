import json
import unittest

from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix import (
    CERT,
    independently_verify,
)


class NonaxisymmetricL1L3MatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_independent_fast_replay(self) -> None:
        independently_verify(False)

    def test_remaining_l1_gate_is_closed(self) -> None:
        rows = [row for row in self.value["candidate_rows"] if row["output_ell"] == 1]
        fixtures = [
            fixture
            for row in rows
            for channel in row["parity_channels"]
            for fixture in channel["basis_fixtures"]
        ]
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(fixtures), 12)
        self.assertTrue(all(fixture["bounded_status"] == "OBSTRUCTED" for fixture in fixtures))
        self.assertTrue(
            all(pairing != "0" for fixture in fixtures for pairing in fixture["scaled_pairings"])
        )

    def test_completion_claim_stays_basis_scoped(self) -> None:
        summary = self.value["matrix_summary"]
        classification = self.value["classification"]
        self.assertEqual(summary["target_adjoint_coefficients"], 56)
        self.assertEqual(summary["nonzero_target_adjoint_coefficients"], 56)
        self.assertTrue(classification["certified_L3_submatrix_replayed"])
        self.assertTrue(classification["all_164_branch_basis_coefficients_classified"])
        self.assertFalse(classification["arbitrary_amplitude_zero_variety_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
