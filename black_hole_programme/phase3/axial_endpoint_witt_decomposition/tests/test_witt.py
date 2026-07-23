from __future__ import annotations

from copy import deepcopy
import json
import unittest

from black_hole_programme.phase3.axial_endpoint_witt_decomposition.verify import (
    CERTIFICATE,
    WittError,
    verify,
    verify_certificate,
)


class EndpointWittTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(CERTIFICATE.read_text())

    def mutated(self) -> dict:
        return deepcopy(self.data)

    def test_certificate(self) -> None:
        verify()

    def test_import_hash_mutation(self) -> None:
        data = self.mutated()
        data["import"]["sha256"] = "0" * 64
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_past_orientation_mutation(self) -> None:
        data = self.mutated()
        data["endpoints"]["Iminus"]["orientation_multiplier"] = 1
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_future_basis_order_mutation(self) -> None:
        data = self.mutated()
        data["endpoints"]["Iplus"]["coordinate_basis"][0:2] = ["XI3", "XI2"]
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_past_Y_mutation(self) -> None:
        data = self.mutated()
        data["endpoints"]["Iminus"]["vectors"]["Y"][1] = "-I*omega"
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_future_Y_mutation(self) -> None:
        data = self.mutated()
        data["endpoints"]["Iplus"]["vectors"]["Y"][1] = (
            "4*(4*omega**2-I*omega-1)"
        )
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_cross_mutation(self) -> None:
        data = self.mutated()
        data["endpoints"]["Iminus"]["E_X_cross"] = "-384*omega/5"
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_inertia_mutation(self) -> None:
        data = self.mutated()
        data["endpoints"]["Iplus"]["witt_split"]["full_inertia"] = [2, 1, 0]
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_second_null_mutation(self) -> None:
        data = self.mutated()
        data["endpoints"]["Iminus"]["second_null_vector_norm"] = "1"
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_interval_mutation(self) -> None:
        data = self.mutated()
        data["declaration"]["frequency_interval"] = ["0", "3/4"]
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_jordan_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["time_translation_Jordan_origin_certified"] = True
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_repeated_factor_promotion_mutation(self) -> None:
        data = self.mutated()
        data["claim_flags"]["repeated_factor_origin_certified"] = True
        with self.assertRaises(WittError):
            verify_certificate(data)

    def test_boundary_deletion_mutation(self) -> None:
        data = self.mutated()
        data["does_not_establish"].remove(
            "that E, X or Y originates from a radial Jordan chain or spectral derivative"
        )
        with self.assertRaises(WittError):
            verify_certificate(data)


if __name__ == "__main__":
    unittest.main()
