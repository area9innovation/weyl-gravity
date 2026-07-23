from __future__ import annotations

from copy import deepcopy
import json
import unittest

from black_hole_programme.phase3.axial_repeated_factor_audit.verify import (
    CERTIFICATE,
    AuditError,
    verify,
    verify_certificate,
    verify_derivative_identities,
)


class RepeatedFactorAuditTests(unittest.TestCase):
    def test_certificate(self) -> None:
        verify()

    def test_derivative_identities(self) -> None:
        verify_derivative_identities()

    def test_dimension_mutation(self) -> None:
        data = json.loads(CERTIFICATE.read_text())
        data["dimension_obstruction"]["complete_Bach_solution_dimension"] = 4
        with self.assertRaises(AuditError):
            verify_certificate(data)

    def test_carrier_exponent_mutation(self) -> None:
        data = json.loads(CERTIFICATE.read_text())
        data["endpoint_obstruction"]["Ricci_carrier_horizon_exponents"][-1] = (
            "-4*I*omega"
        )
        with self.assertRaises(AuditError):
            verify_certificate(data)

    def test_time_jordan_promotion_mutation(self) -> None:
        data = json.loads(CERTIFICATE.read_text())
        data["claim_flags"]["time_translation_Jordan_chain_certified"] = True
        with self.assertRaises(AuditError):
            verify_certificate(data)

    def test_matrix_square_promotion_mutation(self) -> None:
        data = json.loads(CERTIFICATE.read_text())
        data["claim_flags"]["identical_matrix_factor_square_certified"] = True
        with self.assertRaises(AuditError):
            verify_certificate(data)

    def test_weakened_nonlocal_boundary_mutation(self) -> None:
        data = json.loads(CERTIFICATE.read_text())
        data["does_not_establish"].remove(
            "nonexistence of every singular, nonlocal or frequency-dependent matrix equivalence"
        )
        with self.assertRaises(AuditError):
            verify_certificate(data)

    def test_import_hash_mutation(self) -> None:
        data = json.loads(CERTIFICATE.read_text())
        data["imports"]["complete_reconstruction"]["sha256"] = "0" * 64
        with self.assertRaises(AuditError):
            verify_certificate(data)


if __name__ == "__main__":
    unittest.main()
