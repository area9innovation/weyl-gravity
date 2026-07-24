"""Mutation tests for the common moving-frame checkpoint."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class MovingFrameMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate_verifies(self) -> None:
        verify(copy.deepcopy(self.document))

    def test_rejects_rank_promotion_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["rank_three_minor"]["determinant_nonzero"] = False
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_kplus_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["endpoint_normalization_audit"][
            "analytic_first_jet_K_plus"
        ][0][1] = "1"
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_downstream_promotion(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["T_plus_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(changed)


if __name__ == "__main__":
    unittest.main()
