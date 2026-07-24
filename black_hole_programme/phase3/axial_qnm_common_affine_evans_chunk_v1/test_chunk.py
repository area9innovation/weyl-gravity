"""Materialized scoped tests for the panels 0--15 Evans chunk."""
from __future__ import annotations

import json
import unittest

from flint import arb

from .chunk import RUN


class EvansChunkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(RUN.read_text())

    def test_exact_requested_chunk_completed(self) -> None:
        self.assertEqual(self.document["requested_panels"], [0, 15])
        self.assertEqual(self.document["completed_panel_count"], 16)
        self.assertTrue(self.document["all_requested_panels_nonzero"])

    def test_shared_generator_per_panel(self) -> None:
        for row in self.document["rows"]:
            generator = row["omega_generator_id"]
            self.assertEqual(generator, row["horizon"]["omega_generator_id"])
            self.assertEqual(generator, row["outgoing"]["omega_generator_id"])

    def test_every_modulus_lower_is_positive(self) -> None:
        for row in self.document["rows"]:
            self.assertEqual(row["boundary_nonvanishing"]["status"], "PASS")
            self.assertGreater(
                arb(row["physical_mismatch"]["modulus_lower"]).lower(), 0
            )

    def test_argument_principle_not_run(self) -> None:
        self.assertEqual(
            self.document["argument_principle"]["status"], "NOT_RUN"
        )


if __name__ == "__main__":
    unittest.main()
