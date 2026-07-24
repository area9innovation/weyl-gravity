#!/usr/bin/env python3
"""Scoped tests for the horizon reciprocal checkpoint rail."""
from __future__ import annotations

import unittest

from flint import acb, arb, ctx

from .checkpoint_transport import continue_panel, parse_acb, snapshot


class CheckpointTransportTest(unittest.TestCase):
    def setUp(self) -> None:
        ctx.prec = 128

    def test_acb_round_trip(self) -> None:
        value = acb(arb("[1 +/- 0.01]"), arb("[-2 +/- 0.02]"))
        reparsed = parse_acb(str(value))
        self.assertTrue(reparsed.overlaps(value))

    def test_shared_inverse_derivative_snapshot(self) -> None:
        result = snapshot(
            acb(2 + 1j), acb(3 - 2j), acb(-1 + 4j),
            arb("0.01"), arb("0.02"), arb("0.03"),
        )
        self.assertTrue(result["q_recovery_denominator_excludes_zero"])
        self.assertIsNotNone(result["q_recovered"])

    def test_panel_zero_reaches_all_checkpoints(self) -> None:
        result = continue_panel(0)
        self.assertTrue(result["reached_r32"])
        self.assertEqual(
            [item["radius"] for item in result["checkpoints"]],
            [8, 16, 32],
        )


if __name__ == "__main__":
    unittest.main()
