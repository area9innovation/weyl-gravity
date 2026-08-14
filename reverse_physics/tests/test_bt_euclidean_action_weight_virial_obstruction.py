"""Tests for the BT action-weight threshold and virial obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_action_weight_virial_obstruction import (
    ALTERNATING_MODE,
    CERT_PATH,
    EXPECTED_ACTION,
    EXPECTED_DETERMINANT,
    EXPECTED_G_G,
    LOWEST_MODE,
    MEAN_ZERO_BASIS,
    VIRIAL_SHAPE,
    build,
    center_action,
    directional_hessian,
    evaluate_laurent,
    gram_determinant,
    virial_fixture,
)
from reverse_physics.verify_bt_euclidean_action_weight_virial_obstruction import (
    full_lattice_forms,
    verify,
)


class ExactCalculationTests(unittest.TestCase):
    def test_complete_mean_zero_basis(self) -> None:
        self.assertTrue(all(sum(vector) == 0 for vector in MEAN_ZERO_BASIS))
        self.assertEqual(gram_determinant(MEAN_ZERO_BASIS), 3456)

    def test_exact_schur_fixture(self) -> None:
        parameter = 2
        x = 2 ** (3 * parameter)
        hh = directional_hessian(parameter, LOWEST_MODE, LOWEST_MODE)
        hg = directional_hessian(parameter, LOWEST_MODE, ALTERNATING_MODE)
        gg = directional_hessian(parameter, ALTERNATING_MODE, ALTERNATING_MODE)
        determinant = hh * gg - hg * hg
        self.assertEqual(determinant, evaluate_laurent(EXPECTED_DETERMINANT, x))
        self.assertEqual(gg, evaluate_laurent(EXPECTED_G_G, x))
        self.assertEqual(center_action(parameter), evaluate_laurent(EXPECTED_ACTION, x))
        self.assertGreater(determinant / gg, 0)
        self.assertLess(determinant / gg, Fraction(48, x))

    def test_full_lattice_checker(self) -> None:
        forms = full_lattice_forms(
            1,
            LOWEST_MODE,
            ALTERNATING_MODE,
            (MEAN_ZERO_BASIS[1], MEAN_ZERO_BASIS[3], MEAN_ZERO_BASIS[4]),
        )
        self.assertEqual(
            forms["hh"],
            216 * directional_hessian(1, LOWEST_MODE, LOWEST_MODE),
        )
        self.assertEqual(forms["action"], 216 * center_action(1))
        self.assertEqual(forms["other_h"], [0, 0, 0])

    def test_exact_virial_upper_bound(self) -> None:
        self.assertEqual(sum(VIRIAL_SHAPE), 0)
        fixture = virial_fixture()
        upper = Fraction(
            fixture["certified_upper_bound_for_D_over_A"]["numerator"],
            fixture["certified_upper_bound_for_D_over_A"]["denominator"],
        )
        self.assertLess(upper, 2)


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

    def test_mutation_mode(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["lattice_and_symmetry"]["lowest_mode_h"].__setitem__(
                0, 3
            )
        )

    def test_mutation_schur(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_full_low_mode_schur"]["fixtures"][1][
                "full_low_mode_schur_per_spatial_site"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_weight_threshold(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["action_weight_threshold"].__setitem__(
                "quarter_power_status", "OPEN"
            )
        )

    def test_mutation_virial(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["radial_virial_obstruction"]["fixture"][
                "certified_upper_bound_for_D_over_A"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_disposition(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment_bound", "PROVED"
            )
        )

    def test_mutation_dependency(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].__setitem__(
                1, "LORENTZIAN-CAUSAL"
            )
        )

    def test_mutation_provenance(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["provenance"]["inputs"][0].__setitem__(
                "sha256", "0" * 64
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
