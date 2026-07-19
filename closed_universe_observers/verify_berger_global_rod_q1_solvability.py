#!/usr/bin/env python3
"""Replay the exported global-rod q1 primitives without solving again."""

from __future__ import annotations

import json

import sympy as sp

from closed_universe_observers import generate_berger_global_rod_q1_solvability as result


def main() -> int:
    payload = json.loads(result.CERTIFICATE.read_text())
    q1 = json.loads(result.RETAINED_Q1.read_text())["q1_blocks"]["H_retained"]
    for name, frequency, harmonic in (
        ("zero", sp.S.Zero, "zero"),
        ("positive", 2 * result.OMEGA, "positive"),
    ):
        block = payload["exact_blocks"][name]
        operator = result._operator_matrix(q1, frequency)
        sources = result._source_basis(harmonic)
        primitives = sp.zeros(100, 3)
        for column, records in enumerate(block["canonical_primitives_sparse"]):
            for row, raw in records:
                primitives[row, column] = sp.sympify(raw)
        residual = (operator * primitives + sources).applyfunc(sp.simplify)
        if residual != sp.zeros(100, 3):
            raise AssertionError(f"{name} sparse primitive replay failed")
        if block["operator_rank"] != len(block["operator_pivot_columns"]):
            raise AssertionError(f"{name} pivot witness count drifted")
        if block["augmented_ranks"] != [block["operator_rank"]] * 3:
            raise AssertionError(f"{name} augmented ranks do not certify solvability")
        full_stress_mutation = (operator * primitives + 2 * sources).applyfunc(sp.simplify)
        mutation_count = sum(value != 0 for value in full_stress_mutation)
        if mutation_count != block["full_stress_mutation_residual_nonzero_count"]:
            raise AssertionError(f"{name} full-stress normalization mutation drifted")
    flags = payload["flags"]
    if not flags["GLOBAL_ROD_BACKREACTION_SOLVABLE_THROUGH_ORDER_EPSILON_R_SQUARED"]:
        raise AssertionError("second-order solvability flag dropped")
    if not flags["ACTION_EULER_HALF_STRESS_NORMALIZATION_CERTIFIED"]:
        raise AssertionError("action-derived half-stress normalization flag dropped")
    if flags["FULL_NONLINEAR_BACKREACTED_ROD_BRANCH_CERTIFIED"] or flags["84_ROW_INTERACTING_COMPLEX_CERTIFIED"]:
        raise AssertionError("nonlinear result was over-promoted")
    print("BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
