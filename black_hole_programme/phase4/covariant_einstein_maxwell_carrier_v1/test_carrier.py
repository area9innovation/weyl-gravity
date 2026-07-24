#!/usr/bin/env python3
"""Mutation tests for the covariant carrier certificate."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .verify import CERT, verify


class CovariantCarrierTests(unittest.TestCase):
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

    def test_bach_coefficient_mutation_fails(self) -> None:
        self.reject(
            lambda c: c["schouten_carrier"]["expanded_coefficient_basis"].__setitem__(
                "Hessian_psi", "-1/3"
            )
        )

    def test_factorization_sign_mutation_fails(self) -> None:
        self.reject(
            lambda c: c["schouten_carrier"].__setitem__(
                "factorization", "deltaB_ab[h]=+deltaG_ab[q[h]]"
            )
        )

    def test_weyl_gradient_mutation_fails(self) -> None:
        self.reject(
            lambda c: c["source_weyl_to_maxwell_gauge"].__setitem__(
                "q_shift", "-Hessian(Phi)+(1/2)*g*Box(Phi)"
            )
        )

    def test_maxwell_sign_mutation_fails(self) -> None:
        self.reject(
            lambda c: c["quadratic_action"].__setitem__(
                "relative_sign", "S_spin1=+8*alpha*S_Maxwell modulo boundary terms"
            )
        )

    def test_all_ell_promotion_fails(self) -> None:
        self.reject(
            lambda c: c["claim_flags"].__setitem__("all_ell_lift_certified", True)
        )


if __name__ == "__main__":
    unittest.main()
