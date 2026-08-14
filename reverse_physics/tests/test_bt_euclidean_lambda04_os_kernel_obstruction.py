"""Tests and mutation rail for the exact BT lambda=0.4 OS obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_lambda04_os_kernel_obstruction import (
    CERT_PATH,
    build,
    reduced_action,
)
from reverse_physics.verify_bt_euclidean_lambda04_os_kernel_obstruction import (
    full_lattice_action,
    verify,
)


class ExactProducerTests(unittest.TestCase):
    def test_rational_action_gap(self) -> None:
        p = (-7, 0, 7)
        q = (-6, 3, 3)
        spp = reduced_action(p, p)[0]
        sqq = reduced_action(q, q)[0]
        spq = reduced_action(p, q)[0]
        self.assertEqual(spp + sqq - 2 * spq, Fraction(717075, 4096))
        self.assertGreater(spp + sqq - 2 * spq, 0)

    def test_full_lattice_checker_is_distinct(self) -> None:
        p = (-7, 0, 7)
        q = (-6, 3, 3)
        gap = (
            full_lattice_action(p, p)
            + full_lattice_action(q, q)
            - 2 * full_lattice_action(p, q)
        )
        self.assertEqual(gap, Fraction(19361025, 512))


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

    def test_mutation_half_center(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["finite_volume_kernel_obstruction"][
                "half_centers"
            ]["p"].__setitem__(0, -6)
        )

    def test_mutation_full_action(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["finite_volume_kernel_obstruction"][
                "full_actions"
            ]["S_pq"].__setitem__("numerator", 1)
        )

    def test_mutation_gap_sign(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["finite_volume_kernel_obstruction"][
                "log_kernel_convexity_gap_full_lattice"
            ].__setitem__("numerator", -19361025)
        )

    def test_mutation_lambda_0p4_disposition(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["disposition"].__setitem__(
                "ordinary_os_reflection_positivity_at_lambda_0p4", "OPEN"
            )
        )

    def test_mutation_lorentzian_tag(self) -> None:
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

    def test_mutation_extra_top_level_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
