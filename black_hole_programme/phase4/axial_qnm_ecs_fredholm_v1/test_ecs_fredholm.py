"""Mutation tests for the global ECS Fredholm certificate."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify_document

HERE = Path(__file__).resolve().parent


class EcsFredholmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        verify_document(self.data)

    def test_index_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["asymptotic_dichotomy"]["audit"]["fredholm_index"] = 1
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_tangent_domain_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["claim_flags"]["generalized_jost_tangent_in_fixed_domain"] = False
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_pole_rank_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["resolvent_statement"]["principal_rank"] = 2
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_causal_promotion_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["claim_flags"]["lorentzian_causal_resolvent_certified"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_retarded_promotion_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["claim_flags"]["retarded_contour_deformation_certified"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_import_hash_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["imports"]["ecs_inverse_tortoise"]["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            verify_document(data)


if __name__ == "__main__":
    unittest.main()
