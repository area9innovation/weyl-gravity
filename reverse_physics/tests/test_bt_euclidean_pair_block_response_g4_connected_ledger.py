"""Tests for the BT pair-block order-lambda4 connected ledger."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_pair_block_response_g4_connected_ledger import (
    CERT_PATH,
    annealed_g4_ledger,
    build,
    conditional_center_response,
    conditional_ledger,
)
from reverse_physics.verify_bt_euclidean_pair_block_response_g4_connected_ledger import (
    direct_response,
    verify,
)


class ExactLedgerTests(unittest.TestCase):
    def test_zero_background_exact_values(self) -> None:
        longitudinal, affected, counts = conditional_center_response(0)
        transverse, affected_t, counts_t = conditional_center_response(1)
        self.assertEqual((affected, affected_t), (16, 16))
        self.assertEqual(counts, counts_t)
        self.assertEqual(longitudinal[2], Fraction(-7349, 379456))
        self.assertEqual(transverse[2], Fraction(-7979, 379456))
        self.assertEqual(longitudinal[4], Fraction(297291527, 329112813568))
        self.assertEqual(transverse[4], Fraction(342682355, 329112813568))

    def test_nonimporting_direct_expansion_agrees(self) -> None:
        for axis in (0, 1):
            response, affected, counts = conditional_center_response(axis)
            direct, direct_affected, direct_counts = direct_response(axis)
            self.assertEqual((response, affected, counts), (direct, direct_affected, direct_counts))

    def test_conditional_degree_bound(self) -> None:
        rows = conditional_ledger()
        self.assertEqual(sum(row["order"] == 4 for row in rows), 5)
        self.assertTrue(all(row["maximum_background_degree_after_response"] == row["order"] for row in rows))

    def test_outer_ledger_has_two_loop_cap(self) -> None:
        rows = annealed_g4_ledger()
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(row["maximum_loop_rank"] == 2 for row in rows))


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

    def test_mutation_loop_rank(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["two_loop_theorem"].__setitem__("maximum_free_background_loop_rank", 3))

    def test_mutation_g4_fraction(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["zero_background_checkpoint"]["orientation_averaged_lambda4"].__setitem__("numerator", 1))

    def test_mutation_full_coefficient_promotion(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["method_disposition"].__setitem__("full_gibbs_finite_volume_g4_coefficient", "COEFFICIENT_COMPUTED"))

    def test_mutation_dependency_boundary(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_mutation_extra_top_level_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
