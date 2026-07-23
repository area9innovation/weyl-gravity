from __future__ import annotations

from copy import deepcopy
import json
import unittest

from black_hole_programme.phase3.axial_boundary_devissage_no_growth.verify import (
    BoundaryDevissageError,
    CERTIFICATE,
    verify,
    verify_certificate,
)


class BoundaryDevissageTests(unittest.TestCase):
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
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_phase_mutation(self) -> None:
        data = self.mutated()
        data["declaration"]["growth_domain"] = "Im(omega)>0"
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_horizon_amplitude_mutation(self) -> None:
        data = self.mutated()
        data["local_boundary_maps"]["future_horizon"][
            "spin_one_horizon_amplitude"
        ] = "1"
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_outgoing_quotient_mutation(self) -> None:
        data = self.mutated()
        data["local_boundary_maps"]["pure_outgoing_infinity"][
            "spin_one_quotient_amplitudes"
        ]["XI2"] = "1"
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_metric_outgoing_mutation(self) -> None:
        data = self.mutated()
        data["local_boundary_maps"]["pure_outgoing_infinity"][
            "metric_spin_two_outgoing_amplitude"
        ] = "1"
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_full_no_growth_demotion(self) -> None:
        data = self.mutated()
        data["claim_flags"][
            "full_six_state_no_LHP_growing_separated_modes_certified"
        ] = False
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_UHP_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["upper_half_plane_Evans_status_certified"] = True
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_special_point_promotion_mutation(self) -> None:
        data = self.mutated()
        data["upper_half_plane_frame_events"]["regularized_Evans_status"] = (
            "ALL_ARE_ZEROS"
        )
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_Smith_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["simple_QNM_extension_Smith_case_certified"] = True
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_Smith_case_mutation(self) -> None:
        data = self.mutated()
        data["simple_spin_two_QNM_extension_gate"]["Smith_cases"][
            "Gamma_star_nonzero"
        ] = "diag(delta,delta)"
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_Smith_valuation_mutation(self) -> None:
        data = self.mutated()
        data["simple_spin_two_QNM_extension_gate"]["valuation_formula"][
            "first_Smith_valuation"
        ] = "m"
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_spectral_derivative_promotion_mutation(self) -> None:
        data = self.mutated()
        data["simple_spin_two_QNM_extension_gate"][
            "spectral_derivative_status"
        ] = "CERTIFIED with q nonzero"
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_two_ended_surjectivity_overclaim_mutation(self) -> None:
        data = self.mutated()
        data["boundary_devissage"]["boundary_exactness"] = (
            "The two-ended quotient map is surjective."
        )
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)

    def test_boundary_deletion_mutation(self) -> None:
        data = self.mutated()
        data["does_not_establish"].remove(
            "absence of damped upper-half-plane quasinormal or Evans zeros"
        )
        with self.assertRaises(BoundaryDevissageError):
            verify_certificate(data)


if __name__ == "__main__":
    unittest.main()
