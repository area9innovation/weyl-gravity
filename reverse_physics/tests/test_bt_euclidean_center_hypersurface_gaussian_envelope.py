"""Tests for the BT center-hypersurface Gaussian-envelope certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_center_hypersurface_gaussian_envelope import (
    CERT_PATH,
    build,
    gaussian_tube_fixture,
)
from reverse_physics.verify_bt_euclidean_center_hypersurface_gaussian_envelope import (
    independent_gaussian_tube,
    verify,
)


class ExactCountermodelTests(unittest.TestCase):
    def test_producer_fixture(self) -> None:
        exact = gaussian_tube_fixture()
        self.assertEqual(exact["center_variance"], Fraction(25, 4))
        self.assertEqual(exact["total_t_variance"], Fraction(13, 2))
        self.assertEqual(exact["mean_action"], 26)
        self.assertEqual(exact["jacobian_product"], 1)

    def test_independent_fixture(self) -> None:
        exact = independent_gaussian_tube()
        self.assertEqual(exact["a"], Fraction(24, 25))
        self.assertEqual(exact["variance_center"], Fraction(25, 4))
        self.assertEqual(exact["expected_energy"], 26)
        self.assertEqual(exact["jacobian_product"], 1)


class CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.certificate = json.load(handle)

    def test_deterministic_builder(self) -> None:
        self.assertEqual(build(), self.certificate)

    def test_independent_verifier(self) -> None:
        self.assertTrue(verify(CERT_PATH))

    def assert_mutation_rejected(self, mutate) -> None:
        changed = copy.deepcopy(self.certificate)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        try:
            mutate(changed)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_mutation_gaussian_exponent(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["bt_integrated_fiber_envelope"].__setitem__(
                "pointwise_envelope",
                "Z_eta<=3*sqrt(pi/(N*omega_L^2))*exp[-N*omega_L^2*m(eta)^2/9]",
            )
        )

    def test_mutation_center_variance(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_gaussian_tube_countermodel"][
                "r5_fixture"
            ]["center_variance"].__setitem__("numerator", 24)
        )

    def test_mutation_normalized_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "normalized_lowest_mode_second_moment", "PROVED"
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "PROVED"
            )
        )

    def test_mutation_dependency(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
