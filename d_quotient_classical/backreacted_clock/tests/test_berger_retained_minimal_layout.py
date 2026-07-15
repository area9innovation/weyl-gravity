from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.berger_retained_minimal_layout import (
    BergerRetainedMinimalLayout,
)


class BergerRetainedMinimalLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = BergerRetainedMinimalLayout.build()
        cls.payload = cls.result.payload

    def test_component_inventory_and_degrees(self) -> None:
        rows = self.payload["component_rows"]
        self.assertEqual(len(rows), 26)
        self.assertEqual(
            {degree: sum(row["degree"] == degree for row in rows) for degree in (-1, 0, 1, 2)},
            {-1: 3, 0: 10, 1: 10, 2: 3},
        )

    def test_dual_involution(self) -> None:
        rows = {row["row_id"]: row for row in self.payload["component_rows"]}
        for row in rows.values():
            dual = rows[row["dual_row_id"]]
            self.assertEqual(dual["dual_row_id"], row["row_id"])
            self.assertEqual(row["degree"] + dual["degree"], 1)

    def test_gate_split(self) -> None:
        gates = self.payload["gate_split"]
        self.assertEqual(gates["immediate_gate"], "BERGER_RETAINED_MINIMAL_OPERATOR")
        self.assertEqual(gates["subsequent_gate"], "BERGER_NONMINIMAL_COMPLETION")

    def test_open_claims_remain_false(self) -> None:
        flags = self.payload["flags"]
        self.assertFalse(flags["retained_q1_coefficients_complete"])
        self.assertFalse(flags["nonminimal_rows_complete"])
        self.assertFalse(flags["stability_proved"])
        self.assertFalse(flags["causal_green_homotopy_constructed"])
        nonlinear = self.payload["nonlinear_export_compatibility"]
        self.assertFalse(nonlinear["q2_complete"])
        self.assertFalse(nonlinear["satisfies_CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT"])


if __name__ == "__main__":
    unittest.main()
