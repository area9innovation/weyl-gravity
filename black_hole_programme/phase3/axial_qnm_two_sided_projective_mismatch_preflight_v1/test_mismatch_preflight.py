#!/usr/bin/env python3
"""Scoped tests for the physical projective mismatch assembly."""
from __future__ import annotations

import unittest

from flint import ctx

from .mismatch_preflight import panel_mismatch


class MismatchPreflightTest(unittest.TestCase):
    def setUp(self) -> None:
        ctx.prec = 128

    def test_opposite_phase_correction_is_present(self) -> None:
        row = panel_mismatch(0)
        self.assertEqual(row["phase_formula"], "Delta=q_H-q_out+2*I*omega")
        self.assertEqual(
            row["delta_omega"]["formula"],
            "q_H_omega-q_out_omega+2*I",
        )

    def test_first_panel_fails_closed(self) -> None:
        self.assertFalse(panel_mismatch(0)["delta"]["excludes_zero"])


if __name__ == "__main__":
    unittest.main()
