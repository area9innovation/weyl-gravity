from __future__ import annotations

import unittest

from d_quotient_classical.relative.einstein_weyl_relative_316_row_cotangent_completion import build, build_layout
from d_quotient_classical.relative.verify_einstein_weyl_relative_316_row_cotangent_completion import verify


class Relative316CotangentCompletionTest(unittest.TestCase):
    def test_degree_census_and_bundle_selection(self) -> None:
        value, layout = build()
        self.assertEqual(layout["degree_ranks"], [10, 51, 97, 97, 51, 10])
        self.assertEqual(value["bundle_classification"]["selected_added_rows"], 78)
        self.assertFalse(value["bundle_classification"]["rank_only_profile_is_canonical_bundle_completion"])

    def test_pairing_is_exhaustive_and_degree_one(self) -> None:
        layout = build_layout()
        rows = {row["index"]: row for row in layout["rows"]}
        self.assertEqual(len(layout["odd_pairing"]), 316)
        for row in rows.values():
            self.assertEqual(row["degree"] + rows[row["dual_row"]]["degree"], 1)

    def test_downstream_gates_fail_closed(self) -> None:
        value, _layout = build()
        self.assertTrue(value["classification"]["canonical_316_row_unary_cyclic_carrier_exists"])
        self.assertFalse(value["classification"]["complete_q2_on_316_rows"])
        self.assertFalse(value["classification"]["action_current_pairing_transport_complete"])
        self.assertFalse(value["classification"]["causal_green_data"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
