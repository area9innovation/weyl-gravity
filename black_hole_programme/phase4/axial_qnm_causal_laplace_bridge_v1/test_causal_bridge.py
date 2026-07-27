"""Mutation tests for the causal Laplace/resonance bridge."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify_document

HERE = Path(__file__).resolve().parent


class CausalLaplaceBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        verify_document(self.data)

    def test_dependency_tag_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["dependency_tags"] = ["REDUCED-MODE"]
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_pole_demotion_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["meromorphic_continuation"]["principal_nonzero"] = False
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_full_bv_promotion_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["claim_flags"]["full_metric_bv_retarded_propagator_certified"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_contour_promotion_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["claim_flags"][
            "global_inverse_laplace_contour_deformation_certified"
        ] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_real_source_promotion_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["claim_flags"]["real_causal_source_nonannihilation_certified"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_import_hash_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["imports"]["global_ecs_fredholm"]["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            verify_document(data)


if __name__ == "__main__":
    unittest.main()
