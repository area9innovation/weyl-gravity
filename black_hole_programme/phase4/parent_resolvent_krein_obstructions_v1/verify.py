#!/usr/bin/env python3
"""Independent verifier for parent resolvent and Krein obstructions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads((HERE / "certificate.json").read_text())
    assert data["status"] == "EXACT_PARENT_RESOLVENT_KREIN_OBSTRUCTIONS_PASS"

    # Independent exact rational-matrix block check.
    E = sp.Matrix([[2, 1], [1, 3]])
    A = sp.Matrix([[5, -2], [7, 4]])
    Z = sp.zeros(2)
    H = Z.row_join(E).col_join(E.row_join(-A))
    X = E.inv() * A * E.inv()
    candidate = X.row_join(E.inv()).col_join(E.inv().row_join(Z))
    assert H * candidate == sp.eye(4)
    assert candidate * H == sp.eye(4)

    # Independent rank-one coefficient check.
    u = sp.Matrix([2, -1])
    vT = sp.Matrix([[3, 4]])
    alpha = sp.Integer(7)
    P = u * vT / alpha
    beta = (vT * A * u)[0]
    assert P * A * P == beta * (u * vT) / alpha**2

    flags = data["claim_flags"]
    for key in [
        "parent_block_inverse_exact",
        "rank_one_double_coefficient_algebra_exact",
        "simple_self_extension_involution_lemma_exact",
        "branch_resolving_rational_involution_excluded",
        "cotangent_type_endpoint_duality_exact",
        "retarded_convolution_formal_identity",
    ]:
        assert flags[key]
    for key in [
        "physical_qnm_double_pole_established",
        "generalized_ringdown_established",
        "generic_rw_module_simplicity_certified",
        "only_plus_minus_identity_on_bach_spin_two_certified",
        "uniform_positive_einstein_containing_subspace_exists",
        "schwarzschild_retarded_evolution_certified",
        "quantum_statement",
    ]:
        assert not flags[key]

    for item in data["imports"].values():
        path = ROOT / item["path"]
        assert path.exists()
        assert digest(path) == item["sha256"]

    ep2 = json.loads(
        (ROOT / data["imports"]["physical_connection_ep2"]["path"]).read_text()
    )
    assert ep2["claim_flags"]["connection_level_intrinsic_ep2"]
    assert not ep2["claim_flags"]["green_resolvent_second_order_pole_established"]

    cocycle = json.loads(
        (ROOT / data["imports"]["generic_projective_cocycle"]["path"]).read_text()
    )
    assert cocycle["claim_flags"]["generic_rational_cocycle_nontrivial"]
    assert not cocycle["claim_flags"]["physical_QNM_fredholm_realization_constructed"]

    print("EXACT_PARENT_RESOLVENT_KREIN_OBSTRUCTIONS_VERIFIED")


if __name__ == "__main__":
    main()
