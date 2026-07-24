"""Mutation tests for finite-interval Fredholm promotion A."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify_document

HERE = Path(__file__).resolve().parent


class FredholmPromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        verify_document(self.data)

    def test_smith_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["smith_transfer"]["principal_rank"] = 2
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_time_domain_promotion_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["claim_flags"]["t_exp_iomega_t_term_certified"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_causal_resolvent_promotion_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["claim_flags"]["exterior_spacetime_causal_resolvent_certified"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_import_hash_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["imports"]["spin_one_local_unit"]["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_metric_nonannihilation_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["claim_flags"]["physical_metric_reconstruction_nonzero"] = False
        with self.assertRaises(AssertionError):
            verify_document(data)


if __name__ == "__main__":
    unittest.main()
