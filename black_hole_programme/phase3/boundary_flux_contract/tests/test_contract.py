from __future__ import annotations

import copy
import json
import unittest

from black_hole_programme.phase3.boundary_flux_contract.produce import (
    CERTIFICATE,
    build_certificate,
    canonicalize_boundary_pairing,
)
from black_hole_programme.phase3.boundary_flux_contract.verify import (
    VerificationError,
    verify_document,
)


class BoundaryFluxContractTests(unittest.TestCase):
    def test_generated_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(CERTIFICATE.read_text()), build_certificate())

    def test_independent_verifier_accepts_certificate(self) -> None:
        verify_document(json.loads(CERTIFICATE.read_text()))

    def test_basis_congruence_control(self) -> None:
        result = canonicalize_boundary_pairing(
            [[0, 0]], [[3, -2], [-2, -1]], [[2, 1], [1, 1]]
        )
        self.assertEqual(result["finite_dimension_before"], result["finite_dimension_after"])
        self.assertEqual(result["flux_rank_before"], result["flux_rank_after"])
        self.assertEqual(result["quotient_dimension_before"], result["quotient_dimension_after"])

    def test_orientation_mutation_is_rejected(self) -> None:
        doc = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
        doc["action_derived_current"]["orientation"]["boundary_identity"] = (
            "J_Hplus + J_Iplus + J_Hminus + J_Iminus = 0"
        )
        with self.assertRaises(VerificationError):
            verify_document(doc, verify_hashes=False)

    def test_scattering_promotion_mutation_is_rejected(self) -> None:
        doc = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
        doc["claim_flags"]["scattering_matrix_constructed"] = True
        with self.assertRaises(VerificationError):
            verify_document(doc, verify_hashes=False)

    def test_singular_basis_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            canonicalize_boundary_pairing(
                [[0, 0]], [[1, 0], [0, 1]], [[1, 2], [2, 4]]
            )


if __name__ == "__main__":
    unittest.main()

