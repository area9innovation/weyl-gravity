#!/usr/bin/env python3
"""Scoped tests for the common-affine export audit."""
from __future__ import annotations

import unittest

from flint import ctx

from .audit import REQUIRED_FIELDS, compute


class CommonAffineAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        ctx.prec = 128

    def test_contract_requires_independent_residual(self) -> None:
        self.assertIn("independent_residual_radius", REQUIRED_FIELDS)
        self.assertIn("omega_generator_id", REQUIRED_FIELDS)

    def test_bounded_attempt_stops_at_self_map(self) -> None:
        witness = compute()["bounded_joint_rerun_attempt"]
        self.assertEqual(witness["failure"], "HORIZON_Q_REMAINDER_SELF_MAP")


if __name__ == "__main__":
    unittest.main()
