"""Tests for the symbolic-ell q-minus two-parity resonance matrix."""

from __future__ import annotations

import json
import unittest

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix import (
    OUTPUT,
    build_certificate,
    symbolic_result,
)


class SymbolicEllQminusParityResonanceMatrixTests(unittest.TestCase):
    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build_certificate())

    def test_diagonal_ratio_is_universal(self) -> None:
        result = symbolic_result()
        ell = result["ell"]
        self.assertEqual(sp.factor(result["polar"] + ell * (ell + 1) * result["axial"] / 2), 0)

    def test_cross_coefficient_has_nonzero_norm(self) -> None:
        result = symbolic_result()
        ell = result["ell"]
        expected = ell * (ell - 1) ** 3 * (ell + 1) * (ell + 2)
        self.assertEqual(sp.factor(result["cross_norm"] - expected), 0)

    def test_null_sheets_are_kept_distinct_from_extension(self) -> None:
        payload = build_certificate()
        self.assertTrue(payload["classification"]["nonzero_two_momentum_null_sheets_exist_every_integer_ell_ge_2"])
        self.assertFalse(payload["classification"]["general_all_channel_bounded_extension_on_null_sheets"])
        self.assertEqual(payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
