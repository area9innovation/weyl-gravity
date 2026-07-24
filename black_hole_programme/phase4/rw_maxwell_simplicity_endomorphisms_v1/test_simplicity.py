#!/usr/bin/env python3
"""Mutation and boundary tests for the simplicity certificate."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import sympy as sp

from verify import verify_data


HERE = Path(__file__).resolve().parent


class SimplicityCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def rejected(self, mutation) -> None:
        data = copy.deepcopy(self.data)
        mutation(data)
        self.assertTrue(verify_data(data, check_imports=False))

    def test_authoritative_certificate(self) -> None:
        self.assertEqual(verify_data(copy.deepcopy(self.data)), [])

    def test_mutated_local_exponent_rejected(self) -> None:
        self.rejected(
            lambda d: d["local_exhaustion"]["spin2_exponents"].update(
                {"r0": [-1, 2]}
            )
        )

    def test_mutated_algebraically_special_frequency_rejected(self) -> None:
        self.rejected(
            lambda d: d["spin2_simplicity"].update(
                {
                    "algebraically_special_frequency":
                    "omega=sigma*I*Lambda*(Lambda-2)/10"
                }
            )
        )

    def test_mutated_terminal_ansatz_rejected(self) -> None:
        self.rejected(
            lambda d: d["local_exhaustion"].update(
                {"spin2_endomorphism_ansatz": "q=q0+q1/r"}
            )
        )

    def test_mutated_rank_minor_rejected(self) -> None:
        self.rejected(
            lambda d: d["positive_real_nonsplitting_refinement"].update(
                {"augmented_minor_rows_0_1_2_5": "0"}
            )
        )

    def test_false_simplicity_at_special_point_rejected(self) -> None:
        self.rejected(
            lambda d: d["claim_flags"].update(
                {"spin2_simple_at_algebraically_special_points": True}
            )
        )

    def test_nonlocal_c_overclaim_rejected(self) -> None:
        self.rejected(
            lambda d: d["claim_flags"].update({"nonlocal_c_excluded": True})
        )

    def test_curvature_tail_mutation_breaks_special_control(self) -> None:
        r, ll, sig = sp.symbols("r ll sig", nonzero=True)
        f = 1 - 2 / r
        d = lambda x: sp.factor(f * sp.diff(x, r))
        omega_as = sig * sp.I * ll * (ll - 2) / 12
        prefactor = 1 + 6 / ((ll - 2) * r)
        mutated_v = f * (ll / r**2 - 5 / r**3)
        residual = sp.factor(
            (
                d(d(prefactor))
                + 2 * sp.I * sig * omega_as * d(prefactor)
                - mutated_v * prefactor
            ).subs(sig**2, 1)
        )
        self.assertNotEqual(residual, 0)

    def test_ell2_special_control_exact(self) -> None:
        r, sig = sp.symbols("r sig", nonzero=True)
        f = 1 - 2 / r
        d = lambda x: sp.factor(f * sp.diff(x, r))
        omega_as = 2 * sig * sp.I
        prefactor = 1 + sp.Rational(3, 2) / r
        potential = f * (6 / r**2 - 6 / r**3)
        residual = sp.factor(
            (
                d(d(prefactor))
                + 2 * sp.I * sig * omega_as * d(prefactor)
                - potential * prefactor
            ).subs(sig**2, 1)
        )
        self.assertEqual(residual, 0)


if __name__ == "__main__":
    unittest.main()
