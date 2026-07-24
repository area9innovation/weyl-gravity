#!/usr/bin/env python3
"""Mutation tests for the all-ell threshold certificate."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

try:
    from .verify import CERT, verify
except ImportError:
    from verify import CERT, verify


class AllEllThresholdTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(CERT.read_text())

    def reject(self, mutation) -> None:
        data = copy.deepcopy(self.data)
        mutation(data)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "certificate.json"
            path.write_text(json.dumps(data))
            with self.assertRaises(AssertionError):
                verify(path)

    def test_checked_certificate(self) -> None:
        verify()

    def test_horizon_normalization_mutation_fails(self) -> None:
        self.reject(
            lambda c: c["regular_solution"].__setitem__(
                "horizon_normalization", "phi_s_ell(2)=2"
            )
        )

    def test_ell2_control_mutation_fails(self) -> None:
        self.reject(
            lambda c: c["regular_solution"]["ell2_controls"].__setitem__(
                "spin2", "r**3/4"
            )
        )

    def test_jost_promotion_fails(self) -> None:
        self.reject(
            lambda c: c["claim_flags"].__setitem__(
                "uniform_low_frequency_jost_asymptotics", True
            )
        )

    def test_outgoing_interval_promotion_fails(self) -> None:
        self.reject(
            lambda c: c["claim_flags"].__setitem__(
                "punctured_threshold_outgoing_invertibility", True
            )
        )

    def test_all_ell_lift_promotion_fails(self) -> None:
        self.reject(
            lambda c: c["claim_flags"].__setitem__("all_ell_bach_lift", True)
        )


if __name__ == "__main__":
    unittest.main()
