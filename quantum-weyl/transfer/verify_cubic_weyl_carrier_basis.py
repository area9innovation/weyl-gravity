#!/usr/bin/env python3
"""Independent replay of the algebraic cubic Weyl carrier certificate."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

from local_bv.curvature import pair_partitions

try:
    from .cubic_weyl_carrier_basis import OUTPUT, ROOT, build, validate
except ImportError:
    from cubic_weyl_carrier_basis import OUTPUT, ROOT, build, validate


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _rank_two(matrix: list[list[dict[str, int]]]) -> bool:
    values = [[_fraction(entry) for entry in row] for row in matrix]
    return len(values) == 2 and len(values[0]) == 2 and (
        values[0][0] * values[1][1] - values[0][1] * values[1][0]
    ) != 0


def verify() -> dict[str, object]:
    stored = json.loads(OUTPUT.read_text())
    rebuilt = build()
    if stored != rebuilt:
        raise ValueError("stored algebraic cubic Weyl carrier certificate is stale")
    validate(stored)

    if len(tuple(pair_partitions(tuple(range(6))))) != 15:
        raise ValueError("independent six-slot perfect-matching count drifted")
    enumeration = stored["chiral_block_enumeration"]
    terminal = [row["status"] for row in enumeration["orbit_ledger"]]
    if sorted(terminal) != [
        "CANONICAL_NONZERO",
        "ZERO_BY_TRACEFREE_BLOCK",
        "ZERO_BY_TRACEFREE_BLOCK",
    ]:
        raise ValueError("independent tracefree orbit disposition drifted")
    if not _rank_two(stored["independence_witness"]["evaluation_matrix"]):
        raise ValueError("independent parity-carrier determinant vanished")

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {reference['path']}")

    mutations = []
    for flag in (
        "DERIVATIVE_DECORATED_CUBIC_WEYL_BASIS_COMPLETE",
        "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED",
        "CUBIC_WEYL_COEFFICIENTS_COMPUTED",
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
        "LORENTZIAN_CERTIFIED",
    ):
        mutation = deepcopy(stored)
        mutation["claim_flags"][flag] = True
        mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["decision"]["independent_cubic_Weyl_form_factors"] = "CERTIFIED"
    mutations.append(mutation)
    for mutation in mutations:
        try:
            validate(mutation)
        except Exception:
            pass
        else:
            raise ValueError("cubic Weyl carrier overclaim mutation was accepted")

    print("algebraic cubic Weyl carrier independent replay: PASS")
    return stored


if __name__ == "__main__":
    verify()
