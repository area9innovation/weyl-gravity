#!/usr/bin/env python3
"""Scoped tests for the reciprocal horizon chart."""
from __future__ import annotations

import unittest

from flint import acb, ctx

from .reciprocal_transport import first_obstruction, reciprocal_continue


class ReciprocalTransportTest(unittest.TestCase):
    def setUp(self) -> None:
        ctx.prec = 128

    def test_shared_derivative_rule(self) -> None:
        q = acb(2 + 3j)
        eta = acb(5 - 2j)
        epsilon = acb("1e-20")
        finite_difference = (
            1 / (q + epsilon * eta) - 1 / q
        ) / epsilon
        self.assertTrue((finite_difference + eta / (q * q)).abs_upper() < 1e-18)

    def test_panel_zero_switch_is_certified(self) -> None:
        result = reciprocal_continue(first_obstruction(0))
        self.assertTrue(result["switch"]["denominator_excludes_zero"])


if __name__ == "__main__":
    unittest.main()
