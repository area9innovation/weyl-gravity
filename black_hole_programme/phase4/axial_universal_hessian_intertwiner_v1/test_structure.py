#!/usr/bin/env python3
"""Mutation tests for the exact universal Hessian/intertwiner certificate."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .verify import CERT, verify


class UniversalStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(CERT.read_text())

    def _mutate_and_reject(self, mutate) -> None:
        bad = copy.deepcopy(self.data)
        mutate(bad)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "certificate.json"
            path.write_text(json.dumps(bad))
            with self.assertRaises(AssertionError):
                verify(path)

    def test_checked_certificate(self) -> None:
        verify()

    def test_hessian_trace_coefficient_mutation_fails(self) -> None:
        self._mutate_and_reject(
            lambda c: c["weyl_action_hessian"].__setitem__(
                "mixed_bulk_hessian_mod_euler",
                "4*alpha*Integral(psi1_ab*psi2**ab-(1/2)*psi1*psi2)",
            )
        )

    def test_horizon_indicial_mutation_fails(self) -> None:
        self._mutate_and_reject(
            lambda c: c["axial_factor_intertwiner"]["indicial_factors"].__setitem__(
                "r=2", "rho*(rho-1)*(rho**2+4*omega**2)"
            )
        )

    def test_ansatz_residual_mutation_fails(self) -> None:
        self._mutate_and_reject(
            lambda c: c["axial_factor_intertwiner"].__setitem__(
                "ansatz_residual", "0"
            )
        )

    def test_nonlocal_promotion_fails(self) -> None:
        self._mutate_and_reject(
            lambda c: c["claim_flags"].__setitem__(
                "nonlocal_intertwiner_excluded", True
            )
        )


if __name__ == "__main__":
    unittest.main()
