"""Mutation tests for the typed outgoing joint-frame verifier."""
from __future__ import annotations

import copy
import json
import unittest

from .verify import HERE, verify


class JointFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        verify(copy.deepcopy(self.document))

    def test_rejects_rank_promotion_loss(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["triangular_minor"]["determinant_nonzero"] = False
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_kplus_promotion(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["validated_analytic_K_plus_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_layout_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["typed_columns"]["E"]["complex_blocks"] = [
            "R_tangent",
            "0",
            "0",
        ]
        with self.assertRaises(RuntimeError):
            verify(changed)


if __name__ == "__main__":
    unittest.main()
