#!/usr/bin/env python3
"""Mutation tests for the Euler-current transgression certificate."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

try:
    from .verify import CERT, verify
except ImportError:  # direct execution from the certificate directory
    from verify import CERT, verify


class EulerTransgressionTests(unittest.TestCase):
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

    def test_euler_coefficient_mutation_fails(self) -> None:
        self.reject(
            lambda c: c["four_dimensional_decomposition"].__setitem__(
                "identity", "C2=E4+2*Ric2-(1/3)*R2"
            )
        )

    def test_transgression_sign_mutation_fails(self) -> None:
        self.reject(
            lambda c: c["euler_transgression"].__setitem__(
                "identity", "omega_E(delta1,delta2)=-d k_E(delta1,delta2)"
            )
        )

    def test_cut_coefficient_mutation_fails(self) -> None:
        self.reject(
            lambda c: c["axial_einstein_cut"].__setitem__(
                "identity", "F_EE^r=-partial_t Q_EE"
            )
        )

    def test_pointwise_promotion_fails(self) -> None:
        self.reject(
            lambda c: c["claim_flags"].__setitem__(
                "monochromatic_current_pointwise_zero", True
            )
        )

    def test_endpoint_interchange_promotion_fails(self) -> None:
        self.reject(
            lambda c: c["claim_flags"].__setitem__(
                "unconditional_endpoint_limit_interchange", True
            )
        )

    def test_mixed_pairing_promotion_fails(self) -> None:
        self.reject(
            lambda c: c["claim_flags"].__setitem__(
                "mixed_einstein_additional_pairing_euler_exact", True
            )
        )


if __name__ == "__main__":
    unittest.main()
