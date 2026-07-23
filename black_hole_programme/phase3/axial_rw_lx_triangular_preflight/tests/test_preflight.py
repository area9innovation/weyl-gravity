from __future__ import annotations

from copy import deepcopy
import json
import unittest

from black_hole_programme.phase3.axial_rw_lx_triangular_preflight.verify import (
    CERTIFICATE,
    FactorError,
    verify,
    verify_certificate,
)


class TriangularFactorPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(CERTIFICATE.read_text())

    def mutated(self) -> dict:
        return deepcopy(self.data)

    def test_certificate(self) -> None:
        verify()

    def test_import_hash_mutation(self) -> None:
        data = self.mutated()
        data["imports"]["complete_reconstruction"]["sha256"] = "0" * 64
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_RW_coefficient_mutation(self) -> None:
        data = self.mutated()
        data["operators"]["L_RW"]["b"] = "-5*(r-1)/(r**2*(r-2))"
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_Lx_coefficient_mutation(self) -> None:
        data = self.mutated()
        data["operators"]["L_x"]["a"] = data["operators"]["L_RW"]["a"]
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_spin_one_weight_mutation(self) -> None:
        data = self.mutated()
        data["operators"]["L_x_spin_one_gauge"]["g"] = "1/(r*(r-2))"
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_spin_one_physical_promotion_mutation(self) -> None:
        data = self.mutated()
        data["operators"]["L_x_spin_one_gauge"][
            "physical_spin_one_state_claim"
        ] = True
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_scalar_factor_mutation(self) -> None:
        data = self.mutated()
        data["carrier_cyclic_elimination"]["scalar_operator"]["D0"] = "0"
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_embedding_mutation(self) -> None:
        data = self.mutated()
        data["carrier_exact_sequence"]["RW_embedding_J"][2][0] = (
            "I/(omega*r)"
        )
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_quotient_mutation(self) -> None:
        data = self.mutated()
        data["carrier_exact_sequence"]["quotient_K"][0][2] = (
            "2*I*omega/(r*(r-2))"
        )
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_triangular_matrix_mutation(self) -> None:
        data = self.mutated()
        data["carrier_exact_sequence"]["transformed_A4"][1][2] = "0"
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_Einstein_RW_map_mutation(self) -> None:
        data = self.mutated()
        data["Einstein_kernel_RW_equivalence"]["U_H1F_to_PsiPsiPrime"][0][1] = "0"
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_extension_witness_mutation(self) -> None:
        data = self.mutated()
        data["complete_six_state_filtration"][
            "natural_gauge_Lx_to_metric_extension_witness"
        ] = "0"
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_direct_sum_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"][
            "complete_direct_RW_square_plus_Lx_decomposition_certified"
        ] = True
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_endpoint_assignment_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["endpoint_Witt_vectors_assigned_to_operator_factors"] = True
        with self.assertRaises(FactorError):
            verify_certificate(data)

    def test_boundary_deletion_mutation(self) -> None:
        data = self.mutated()
        data["does_not_establish"].remove(
            "a radial generalized-mode or time-translation Jordan interpretation"
        )
        with self.assertRaises(FactorError):
            verify_certificate(data)


if __name__ == "__main__":
    unittest.main()
