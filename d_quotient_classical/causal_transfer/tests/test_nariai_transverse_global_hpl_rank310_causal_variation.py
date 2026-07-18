from __future__ import annotations

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_global_hpl_rank310_causal_variation import (
    build,
    finite_hpl_fixture,
    symbolic_representative_comparison,
    verify,
)


class GlobalHPLRank310Tests(unittest.TestCase):
    def test_cyclic_hpl_fixture(self) -> None:
        fixture = finite_hpl_fixture()
        self.assertEqual(len(fixture["identity_defects"]), 14)
        self.assertTrue(all(value == 0 for value in fixture["identity_defects"].values()))
        self.assertGreater(fixture["qdot_nonzero"], 0)

    def test_geometric_representative_match(self) -> None:
        self.assertEqual(
            symbolic_representative_comparison(),
            {"inclusion_dot": 0, "projection_dot": 0, "homotopy_dot": 0, "metric_q_dot": 0},
        )

    def test_scope(self) -> None:
        payload = build()
        verify(payload)
        self.assertTrue(payload["flags"]["TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION"])
        self.assertFalse(payload["flags"]["TRANSVERSE_CAUSAL_TRANSFER"])
        self.assertFalse(payload["flags"]["TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY"])


if __name__ == "__main__":
    unittest.main()
