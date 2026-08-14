"""Tests for the all-background BT lowest-mode theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_all_background_lowest_mode_curvature import CERT_PATH, build, plaquette_surplus
from reverse_physics.verify_bt_euclidean_all_background_lowest_mode_curvature import verify


class ExactTests(unittest.TestCase):
    def test_edge_inequality_fixtures(self) -> None:
        for U, V, A in ((Fraction(2), Fraction(4), Fraction(1, 2)), (Fraction(3, 2), Fraction(5, 3), Fraction(7, 4))):
            retained = Fraction(1, 5) * (
                U**2 + U**-2 - U - U**-1 + V**2 + V**-2 - V - V**-1
            )
            self.assertGreaterEqual(plaquette_surplus(U, V, A), retained)

    def test_builder_is_deterministic(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle), build())


class MutationTests(unittest.TestCase):
    def setUp(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.payload = json.load(handle)

    def reject(self, mutation) -> None:
        changed = copy.deepcopy(self.payload)
        mutation(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_verifier_accepts_certificate(self) -> None:
        self.assertTrue(verify())

    def test_rejects_bernstein_mutation(self) -> None:
        self.reject(lambda data: data["plaquette_absorption"]["derivative_polynomial_bernstein_coefficients"][1].__setitem__("numerator", 28))

    def test_rejects_variance_constant_mutation(self) -> None:
        self.reject(lambda data: data["theorem"]["variance_constant"].__setitem__("numerator", 8))

    def test_rejects_annealed_center_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("annealed_center_second_moment", "PROVED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "PROVED"))

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
