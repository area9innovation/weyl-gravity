"""Scoped tests for stable-root common-affine panels 78--93."""
from __future__ import annotations

import json
import unittest

from flint import arb

from .chunk import RUN


class EvansChunkV6Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(RUN.read_text())

    def test_ordered_prefix(self) -> None:
        rows = self.document["rows"]
        self.assertEqual(
            [row["panel"] for row in rows],
            list(range(78, 78 + len(rows))),
        )

    def test_shared_correlated_exports(self) -> None:
        for row in self.document["rows"]:
            if row["boundary_nonvanishing"]["status"] != "PASS":
                break
            generator = row["omega_generator_id"]
            self.assertEqual(generator, row["horizon"]["omega_generator_id"])
            self.assertEqual(generator, row["outgoing"]["omega_generator_id"])
            for endpoint in ("horizon", "outgoing"):
                self.assertIsNotNone(
                    row[endpoint]["q_tau_polynomial_coefficients"]
                )
                self.assertIsNotNone(
                    row[endpoint]["q_omega_polynomial_coefficients"]
                )

    def test_ordered_stop_and_nonzero(self) -> None:
        rows = self.document["rows"]
        terminal = self.document["terminal"]
        admitted = rows[:-1] if terminal else rows
        for row in admitted:
            self.assertEqual(row["boundary_nonvanishing"]["status"], "PASS")
            self.assertGreater(
                arb(row["physical_mismatch"]["modulus_lower"]).lower(), 0
            )
        if terminal:
            self.assertEqual(rows[-1]["panel"], terminal["panel"])
            self.assertNotEqual(
                rows[-1]["boundary_nonvanishing"]["status"], "PASS"
            )

    def test_no_threshold_relaxation(self) -> None:
        self.assertFalse(self.document["threshold_lowered"])


if __name__ == "__main__":
    unittest.main()
