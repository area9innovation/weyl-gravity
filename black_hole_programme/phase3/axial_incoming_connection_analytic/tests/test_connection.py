from __future__ import annotations

from copy import deepcopy
import json
import unittest

from black_hole_programme.phase3.axial_incoming_connection_analytic.verify import (
    CERTIFICATE,
    ConnectionError,
    verify,
    verify_certificate,
)


class IncomingConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(CERTIFICATE.read_text())

    def mutated(self) -> dict:
        return deepcopy(self.data)

    def test_certificate(self) -> None:
        verify()

    def test_import_hash_mutation(self) -> None:
        data = self.mutated()
        data["imports"]["triangular_factorization"]["sha256"] = "0" * 64
        with self.assertRaises(ConnectionError):
            verify_certificate(data)

    def test_horizon_amplitude_mutation(self) -> None:
        data = self.mutated()
        data["horizon_factor_frame"]["spin_one_quotient_amplitudes"][
            "XH0a"
        ] = "0"
        with self.assertRaises(ConnectionError):
            verify_certificate(data)

    def test_Iminus_amplitude_mutation(self) -> None:
        data = self.mutated()
        data["Iminus_factor_frame"]["spin_one_quotient_amplitudes"]["XI1"] = (
            "2*I*omega"
        )
        with self.assertRaises(ConnectionError):
            verify_certificate(data)

    def test_metric_normalization_mutation(self) -> None:
        data = self.mutated()
        data["Iminus_factor_frame"]["metric_RW_incoming_amplitude"] = "I*omega"
        with self.assertRaises(ConnectionError):
            verify_certificate(data)

    def test_potential_mutation(self) -> None:
        data = self.mutated()
        data["factor_potentials"]["spin_one"]["V1"] = "5*(r-2)/r**3"
        with self.assertRaises(ConnectionError):
            verify_certificate(data)

    def test_prefactor_mutation(self) -> None:
        data = self.mutated()
        data["determinant_theorem"]["rational_prefactor"] = "1"
        with self.assertRaises(ConnectionError):
            verify_certificate(data)

    def test_Tplus_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["Tplus_rank_certified"] = True
        with self.assertRaises(ConnectionError):
            verify_certificate(data)

    def test_reflection_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["reflection_amplitudes_nonzero_certified"] = True
        with self.assertRaises(ConnectionError):
            verify_certificate(data)

    def test_stability_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["upper_half_plane_pole_exclusion_certified"] = True
        with self.assertRaises(ConnectionError):
            verify_certificate(data)

    def test_boundary_deletion_mutation(self) -> None:
        data = self.mutated()
        data["does_not_establish"].remove(
            "invertibility or any fixed rank of the Iplus outgoing/reflection block Tplus"
        )
        with self.assertRaises(ConnectionError):
            verify_certificate(data)


if __name__ == "__main__":
    unittest.main()
