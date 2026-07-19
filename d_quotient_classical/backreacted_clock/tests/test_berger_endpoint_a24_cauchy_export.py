from __future__ import annotations

from copy import deepcopy
import json
import unittest

from d_quotient_classical.backreacted_clock.berger_endpoint_a24_cauchy_export import (
    OUTPUT,
    build,
    verify,
)


class BergerEndpointA24CauchyExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checked = json.loads(OUTPUT.read_text())
        cls.built = build()

    def test_checked_export_reproduces(self) -> None:
        self.assertEqual(self.built, self.checked)

    def test_all_exact_checks_pass(self) -> None:
        self.assertTrue(all(self.built["exact_checks"].values()))

    def test_two_a12_blocks_are_exact(self) -> None:
        blocks = self.built["derived_A12_blocks"]
        self.assertEqual(set(blocks), {"ghost_A12", "identity_A12"})
        self.assertTrue(all(block["shape"] == [12, 12] for block in blocks.values()))
        self.assertTrue(all(block["entries"] for block in blocks.values()))

    def test_internal_hash_mutation_fails_closed(self) -> None:
        mutant = deepcopy(self.built)
        mutant["factor_records"]["F_spatial_K_spatial"]["entries"][0][2][0][1] = "0"
        with self.assertRaises(ValueError):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
