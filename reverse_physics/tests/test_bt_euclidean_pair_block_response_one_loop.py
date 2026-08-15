"""Tests for the BT nearest-neighbour pair-block one-loop result."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_pair_block_response_one_loop import (
    CERT_PATH,
    annealed_pair_kernel,
    build,
    compact_symbol,
    conditional_interactions,
    exact_l6_coefficient,
    large_volume_reduction,
    vacuum_pair_beta,
    walk_lower_bound,
    x_polynomial,
)
from reverse_physics.verify_bt_euclidean_pair_block_response_one_loop import (
    exact_l6,
    raw_pair_kernel,
    verify,
)


class ExactPairCalculationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cubic, cls.quartic, cls.affected = conditional_interactions()
        cls.longitudinal, cls.transverse, cls.averaged = annealed_pair_kernel(
            cls.cubic, cls.quartic
        )

    def test_action_jet_sizes(self) -> None:
        self.assertEqual(self.affected, 16)
        self.assertEqual((len(self.cubic), len(self.quartic)), (314, 701))

    def test_pair_covariance_kernel(self) -> None:
        self.assertEqual(self.averaged.constant, Fraction(12493, 1517824))
        self.assertEqual(len(self.averaged.linear), 202)
        self.assertEqual(sum(self.averaged.linear.values(), Fraction()), 0)

    def test_compact_fourier_numerator(self) -> None:
        self.assertEqual(x_polynomial(self.averaged.linear), compact_symbol())

    def test_vacuum_sign_is_opposite(self) -> None:
        _, _, beta = vacuum_pair_beta(self.cubic, self.quartic)
        self.assertEqual(beta, Fraction(-15643, 1517824))
        self.assertLess(beta, 0)

    def test_exact_l6_two_implementations(self) -> None:
        expected = Fraction(956585197, 10069092633600)
        self.assertEqual(exact_l6_coefficient(self.averaged.constant), expected)
        self.assertEqual(exact_l6(), expected)

    def test_large_volume_rational_margin(self) -> None:
        self.assertEqual(
            large_volume_reduction(),
            (
                Fraction(-32629, 1517824),
                Fraction(1, 14),
                Fraction(39, 1568),
            ),
        )
        lower = walk_lower_bound()["coefficient_lower"]
        self.assertIsInstance(lower, Fraction)
        self.assertGreater(lower, Fraction(1, 10000))

    def test_nonimporting_raw_kernel(self) -> None:
        independent, cubic_terms, quartic_terms, affected = raw_pair_kernel()
        self.assertEqual((cubic_terms, quartic_terms, affected), (314, 701, 16))
        self.assertEqual(independent.constant, self.averaged.constant)
        self.assertEqual(independent.coefficients, self.averaged.linear)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

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

    def test_mutation_l6_sign(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["all_volume_formula"].__setitem__(
                "exact_l6_sign", "STRICTLY_NEGATIVE"
            )
        )

    def test_mutation_large_volume_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["large_volume_decision"][
                "simple_strict_lower"
            ].__setitem__("numerator", 2)
        )

    def test_mutation_kernel_hash(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["conditional_one_loop_derivation"].__setitem__(
                "raw_green_kernel_sha256", "0" * 64
            )
        )

    def test_mutation_fixed_coupling_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "nonperturbative_pair_response_at_lambda_0_4", "PROVED_POSITIVE"
            )
        )

    def test_mutation_dependency_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )

    def test_mutation_extra_top_level_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
