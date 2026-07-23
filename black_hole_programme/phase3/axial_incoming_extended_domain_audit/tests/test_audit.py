from __future__ import annotations

from copy import deepcopy
import json
import unittest

from black_hole_programme.phase3.axial_incoming_extended_domain_audit.verify import (
    CERTIFICATE,
    ExtendedAuditError,
    verify,
    verify_certificate,
)


class ExtendedIncomingAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(CERTIFICATE.read_text())

    def mutated(self) -> dict:
        return deepcopy(self.data)

    def test_certificate(self) -> None:
        verify()

    def test_import_hash_mutation(self) -> None:
        data = self.mutated()
        data["imports"]["formal_grams"]["sha256"] = "0" * 64
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_uniform_bound_mutation(self) -> None:
        data = self.mutated()
        data["uniform_pilot_margin"]["minimum_modulus_squared"] = "2"
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_positive_real_floor_mutation(self) -> None:
        data = self.mutated()
        data["uniform_pilot_margin"]["positive_real_infimum"] = "1/3"
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_gram_mutation(self) -> None:
        data = self.mutated()
        data["factor_adapted_Iminus_gram"]["gram_over_pi_alpha_W"][0][0] = (
            "625/(5*omega)"
        )
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_factor_alignment_warning_mutation(self) -> None:
        data = self.mutated()
        data["factor_adapted_Iminus_gram"]["factor_alignment_warning"] = (
            "old Witt plane is factor aligned"
        )
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_factor_projection_mutation(self) -> None:
        data = self.mutated()
        data["factor_adapted_Iminus_gram"]["factor_projection"]["pi_x(RI)"] = "2"
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_unit_quotient_norm_mutation(self) -> None:
        data = self.mutated()
        data["factor_adapted_Iminus_gram"]["spin_one_quotient_line"][
            "unit_quotient_norm"
        ] = "-31/(15*omega)"
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_weighted_majorant_mutation(self) -> None:
        data = self.mutated()
        data["positive_real_direct_integral"]["spin_one_weight"] = (
            "b(omega)=31/(15*omega)"
        )
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_fractional_space_boundary_mutation(self) -> None:
        data = self.mutated()
        data["positive_real_direct_integral"]["threshold"][
            "point_trace_warning"
        ] = "Finite weighted flux proves s(0)=0 without further assumptions."
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_fundamental_symmetry_promotion_mutation(self) -> None:
        data = self.mutated()
        data["positive_real_direct_integral"]["fundamental_symmetry"][
            "scope"
        ] = "This is Mannheim's BRST-compatible C operator."
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_Witt_gram_mutation(self) -> None:
        data = self.mutated()
        data["factor_adapted_Iminus_gram"][
            "canonical_Witt_gram_over_pi_alpha_W"
        ][1][1] = "1"
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_growth_half_plane_mutation(self) -> None:
        data = self.mutated()
        data["Evans_convention_audit"]["growth_half_plane"] = (
            "Im(omega)>0 because the time factor is exp(+I*omega*t)"
        )
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_UHP_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["no_upper_half_plane_Evans_zeros_certified"] = True
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_special_point_zero_promotion_mutation(self) -> None:
        data = self.mutated()
        data["special_imaginary_points"]["omega=I/2"][
            "genuine_reduced_Evans_zero"
        ] = True
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_Tplus_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["Tplus_or_reflection_nonvanishing_certified"] = True
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_zero_frequency_promotion_mutation(self) -> None:
        data = self.mutated()
        data["positive_real_extension"]["omega_zero_excluded"] = False
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)

    def test_boundary_deletion_mutation(self) -> None:
        data = self.mutated()
        data["does_not_establish"].remove(
            "absence of upper-half-plane damped quasinormal or Evans zeros"
        )
        with self.assertRaises(ExtendedAuditError):
            verify_certificate(data)


if __name__ == "__main__":
    unittest.main()
