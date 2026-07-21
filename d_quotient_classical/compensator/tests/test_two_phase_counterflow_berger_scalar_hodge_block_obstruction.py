from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import sympy as sp


MODULE_PATH = Path(__file__).resolve().parents[1] / (
    "two_phase_counterflow_berger_scalar_hodge_block_obstruction.py"
)
SPEC = importlib.util.spec_from_file_location("scalar_hodge_obstruction", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ScalarHodgeBlockObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate, cls.payload = MODULE.build()

    def test_exact_pbw_defect(self) -> None:
        rows = self.payload["first_closure_test"]["PBW_rows"]
        self.assertEqual([len(row) for row in rows], [5, 6, 6])
        self.assertEqual(
            self.payload["first_closure_test"]["leading_mode_coefficient"],
            "93*I*k/40",
        )

    def test_round_limit_is_a_detected_mutation(self) -> None:
        for operator in MODULE._expected_defect():
            for _, _, coefficient in operator.terms:
                self.assertEqual(sp.simplify(coefficient.subs(MODULE.V, MODULE.U)), 0)

    def test_fail_closed_terminal_status(self) -> None:
        terminal = self.certificate["terminal_verdict"]
        self.assertFalse(terminal["generic_nonzero_k_scalar_subcomplex_closed"])
        self.assertEqual(
            terminal["physical_quotient_status"],
            "NOT_DEFINED_NONCLOSED_SUBCOMPLEX",
        )
        self.assertFalse(terminal["physical_instability_found"])
        self.assertTrue(terminal["q70_parent_nilpotency_and_causality_preserved"])

    def test_exceptional_labels_are_not_promoted(self) -> None:
        statuses = self.certificate["exceptional_statuses"]
        self.assertEqual(statuses["j=0,m=0,k=0"], "EXCEPTIONAL_ZERO_GRADIENT")
        self.assertEqual(
            statuses["integer j>=1, arbitrary m, k=0"],
            "FIRST_DEFECT_VANISHES_FULL_SCALAR_BLOCK_NOT_COMPUTED",
        )

    def test_mutations_are_explicit(self) -> None:
        mutations = {row["id"]: row for row in self.payload["mutation_ledger"]}
        self.assertEqual(
            set(mutations),
            {
                "ROUND_LIMIT_u_EQUALS_v",
                "RIGHT_NEUTRAL_k_EQUALS_0",
                "DROP_HAAR_NORMALIZATION",
                "DROP_WIGNER_CONJUGATION_PHASE",
                "DELETE_GAUGE_FIXED_ANTIGHOST_DUAL_ROW",
            },
        )
        self.assertTrue(all(row["detected"] for row in mutations.values()))


if __name__ == "__main__":
    unittest.main()
