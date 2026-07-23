#!/usr/bin/env python3
"""Mutation tests for the exact local QNM Smith certificate."""
from __future__ import annotations

import copy
import json
import unittest

from .verify import CERTIFICATE, verify_document


class LocalSmithDichotomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(CERTIFICATE.read_text())

    def mutate(self, path: tuple[str, ...], value: object) -> list[str]:
        document = copy.deepcopy(self.document)
        cursor = document
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        return verify_document(document)

    def test_baseline(self) -> None:
        self.assertEqual(verify_document(self.document), [])

    def test_rejects_promoted_beta(self) -> None:
        self.assertTrue(self.mutate(
            ("boundary", "beta_n_evaluated"), True
        ))

    def test_rejects_selected_double_pole(self) -> None:
        self.assertTrue(self.mutate(
            ("claim_flags", "double_resolvent_pole_established"), True
        ))

    def test_rejects_smith_valuation_mutation(self) -> None:
        self.assertTrue(self.mutate(
            (
                "local_dvr_proof",
                "nonzero_class_case",
                "spin_two_pair_valuations",
            ),
            [1, 1],
        ))

    def test_rejects_factor_order_sorted_conflation(self) -> None:
        self.assertTrue(self.mutate(
            (
                "local_dvr_proof",
                "nonzero_class_case",
                "sorted_full_smith_valuations",
            ),
            [0, 2, 0],
        ))

    def test_rejects_elimination_mutation(self) -> None:
        document = copy.deepcopy(self.document)
        document["spin_one_elimination"]["left_matrix"][0][2] = "0"
        self.assertTrue(verify_document(document))

    def test_rejects_fredholm_shift_mutation(self) -> None:
        self.assertTrue(self.mutate(
            (
                "fredholm_invariant",
                "finite_normal_form",
                "beta_shift",
            ),
            "1",
        ))


if __name__ == "__main__":
    unittest.main()
