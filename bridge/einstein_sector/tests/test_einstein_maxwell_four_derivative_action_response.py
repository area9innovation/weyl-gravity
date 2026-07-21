from __future__ import annotations

import json
import unittest

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_four_derivative_action_response import (
    OUTPUT,
    _p_cross_response,
    _response_map,
    build_certificate,
)


class ActionResponseTest(unittest.TestCase):
    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build_certificate())

    def test_complete_quotient_and_no_lift(self) -> None:
        value = build_certificate()
        self.assertEqual(value["basis_reduction"]["quotient_dimension"], 3)
        self.assertFalse(
            value["exact_cokernel"][
                "unrestricted_q_primary_coefficient_system_has_solution"
            ]
        )
        self.assertEqual(
            value["p_shell_cross_response"]["status"],
            "CERTIFIED",
        )
        self.assertEqual(
            value["p_shell_cross_response"]["zero_cross_kernel_dimension"],
            0,
        )

    def test_basis_removal_mutations_reduce_cross_rank(self) -> None:
        cross = _p_cross_response()
        matrix = sp.Matrix(
            [
                [sp.sympify(entry) for entry in row]
                for row in cross["zero_cross_constraint_matrix"]
            ]
        )
        self.assertEqual(matrix.rank(), 6)
        for removed in range(matrix.cols):
            retained = [column for column in range(matrix.cols) if column != removed]
            self.assertEqual(matrix[:, retained].rank(), 5)

    def test_target_mutations_are_not_hardcoded_no_go(self) -> None:
        response = _response_map()
        # A known image point must be admitted by the response map.
        self.assertEqual(
            response["per_invariant"]["F2"]["axial"],
            [["0", "0"], ["0", "-8"]],
        )
        # The two actual target witnesses are independent.
        value = build_certificate()["exact_cokernel"]["witnesses"]
        self.assertEqual(value[0]["on_requested_target"], "-9")
        self.assertEqual(value[1]["on_requested_target"], "-9/4")


if __name__ == "__main__":
    unittest.main()
