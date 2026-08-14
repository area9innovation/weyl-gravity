"""Tests for the BT lowest-mode/UV Schur obstruction certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_low_mode_uv_schur_obstruction import (
    ALTERNATING_MODE,
    CERT_PATH,
    DEGENERATING_DIRECTION,
    EXPECTED_DETERMINANT,
    EXPECTED_G_G,
    LOWEST_MODE,
    build,
    center_action,
    directional_hessian,
    evaluate_laurent,
)
from reverse_physics.verify_bt_euclidean_low_mode_uv_schur_obstruction import (
    full_lattice_forms,
    verify,
)


class ExactCalculationTests(unittest.TestCase):
    def test_mode_decomposition(self) -> None:
        self.assertTrue(all(
            3 * DEGENERATING_DIRECTION[i]
            == -2 * LOWEST_MODE[i] + ALTERNATING_MODE[i]
            for i in range(6)
        ))
        self.assertEqual(
            sum(a * b for a, b in zip(LOWEST_MODE, ALTERNATING_MODE)), 0
        )
        self.assertEqual(
            sum(a * b for a, b in zip(LOWEST_MODE, DEGENERATING_DIRECTION)), -8
        )

    def test_exact_schur_fixture(self) -> None:
        parameter = 3
        x = 2**parameter
        hh = directional_hessian(parameter, LOWEST_MODE, LOWEST_MODE)
        hg = directional_hessian(parameter, LOWEST_MODE, ALTERNATING_MODE)
        gg = directional_hessian(parameter, ALTERNATING_MODE, ALTERNATING_MODE)
        det = hh * gg - hg * hg
        self.assertEqual(det, evaluate_laurent(EXPECTED_DETERMINANT, x))
        self.assertEqual(gg, evaluate_laurent(EXPECTED_G_G, x))
        self.assertGreater(det / gg, 0)
        self.assertLessEqual(det / gg, Fraction(72, x))

    def test_full_lattice_checker(self) -> None:
        forms = full_lattice_forms(
            3, LOWEST_MODE, ALTERNATING_MODE, DEGENERATING_DIRECTION
        )
        self.assertEqual(
            forms["vv"],
            216 * directional_hessian(
                3, DEGENERATING_DIRECTION, DEGENERATING_DIRECTION
            ),
        )
        self.assertEqual(forms["action"], 216 * center_action(3))


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
        mutate(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_mutation_mode(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["lattice_and_modes"]["lowest_mode_h"].__setitem__(
                0, 3
            )
        )

    def test_mutation_schur(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_two_mode_hessian"]["fixtures"][2][
                "low_mode_schur_complement_per_spatial_site"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_laurent(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_two_mode_hessian"][
                "determinant_laurent_coefficients"
            ].__setitem__("3", 287)
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
