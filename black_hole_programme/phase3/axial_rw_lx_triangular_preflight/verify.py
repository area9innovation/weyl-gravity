#!/usr/bin/env python3
"""Exact verifier for the RW/RW/Lx triangular factor filtration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
R, W = sp.symbols("r omega", nonzero=True, real=True)
I = sp.I
P, PP, Q, QP, H1, F = sp.symbols("P Pp Q Qp H1 F")
LOCALS = {
    "r": R,
    "omega": W,
    "I": I,
    "P": P,
    "Pp": PP,
    "Q": Q,
    "Qp": QP,
    "H1": H1,
    "F": F,
}


class FactorError(AssertionError):
    """Raised when an exact factor, map, or claim boundary drifts."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FactorError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals=LOCALS)


def _matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[_expr(value) for value in row] for row in rows])


def _cancel(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def _zero(value: sp.Expr) -> bool:
    return _cancel(value) == 0


def _matrix_zero(matrix: sp.Matrix) -> bool:
    return all(_zero(value) for value in matrix)


def _matrix_equal(left: sp.Matrix, right: sp.Matrix) -> bool:
    return left.shape == right.shape and _matrix_zero(left - right)


def _derivative_row(row: sp.Matrix, connection: sp.Matrix) -> sp.Matrix:
    return (row.diff(R) + row * connection).applyfunc(_cancel)


def _companion(a: sp.Expr, b: sp.Expr) -> sp.Matrix:
    return sp.Matrix([[0, 1], [-b, -a]])


def _compose_second_order(
    outer_a: sp.Expr,
    outer_b: sp.Expr,
    inner_a: sp.Expr,
    inner_b: sp.Expr,
) -> list[sp.Expr]:
    """Return D0..D3 for L(outer) composed with L(inner)."""
    d3 = outer_a + inner_a
    d2 = 2 * sp.diff(inner_a, R) + inner_b + outer_a * inner_a + outer_b
    d1 = (
        sp.diff(inner_a, R, 2)
        + 2 * sp.diff(inner_b, R)
        + outer_a * (sp.diff(inner_a, R) + inner_b)
        + outer_b * inner_a
    )
    d0 = (
        sp.diff(inner_b, R, 2)
        + outer_a * sp.diff(inner_b, R)
        + outer_b * inner_b
    )
    return [_cancel(value) for value in (d0, d1, d2, d3)]


def verify_certificate(data: dict[str, Any]) -> None:
    _require(
        data.get("schema") == "phase3-axial-rw-lx-triangular-preflight-v1",
        "wrong schema",
    )
    _require(data.get("lifecycle") == "CLASSIFIED", "wrong lifecycle")
    _require(
        data.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency boundary drift",
    )
    _require(
        data["declaration"]["domain"]
        == "r>2 and real omega in [1/2,3/4]",
        "domain drift",
    )

    imports: dict[str, dict[str, Any]] = {}
    for name, reference in data["imports"].items():
        path = Path(reference["path"])
        _require(
            not path.is_absolute() and ".." not in path.parts,
            f"unsafe import path: {name}",
        )
        full = ROOT / path
        _require(full.is_file(), f"missing import: {name}")
        _require(_sha256(full) == reference["sha256"], f"hash drift: {name}")
        _require(
            len(reference["commit"]) == 40
            and all(character in "0123456789abcdef" for character in reference["commit"]),
            f"invalid import commit: {name}",
        )
        imports[name] = json.loads(full.read_text())

    complete = imports["complete_reconstruction"]
    A6 = _matrix(complete["complete_reconstruction"]["flow6"])
    _require(A6.shape == (6, 6), "complete flow is not six-dimensional")
    A4 = A6[:4, :4]
    source = A6[4:, :4]
    kernel2 = A6[4:, 4:]
    _require(_matrix_zero(A6[:4, 4:]), "carrier is not a quotient of the full flow")

    rw = data["operators"]["L_RW"]
    lx = data["operators"]["L_x"]
    a_rw, b_rw = _expr(rw["a"]), _expr(rw["b"])
    a_x, b_x = _expr(lx["a"]), _expr(lx["b"])
    A_rw, A_x = _companion(a_rw, b_rw), _companion(a_x, b_x)
    _require(
        not _zero(a_x - a_rw) and not _zero(b_x - b_rw),
        "L_x was falsely made identical to L_RW",
    )
    _require(lx["not_identical_to_L_RW"] is True, "distinct-factor flag drift")

    # Multiplication by g identifies the quotient with the standard ell=2
    # spin-one RW differential equation in ingoing-EF convention.
    spin_one = data["operators"]["L_x_spin_one_gauge"]
    g = _expr(spin_one["g"])
    f = (R - 2) / R
    transformed_a = _cancel(2 * sp.diff(g, R) / g + a_x)
    transformed_b = _cancel(
        sp.diff(g, R, 2) / g
        + a_x * sp.diff(g, R) / g
        + b_x
    )
    _require(
        _zero(transformed_a - (sp.diff(f, R) / f + 2 * I * W / f)),
        "L_x weighted derivative coefficient is not spin-one RW",
    )
    _require(
        _zero(transformed_b + 6 / (R * (R - 2))),
        "L_x weighted potential is not spin-one RW",
    )
    _require(
        _zero(6 * (R - 2) / R**3 - f * 2 * 3 / R**2),
        "displayed ell=2 Maxwell potential drift",
    )
    _require(
        spin_one["classification"]
        == "spin-one/Maxwell Regge-Wheeler-type differential factor"
        and spin_one["physical_spin_one_state_claim"] is False,
        "spin-one factor was physically overinterpreted",
    )

    # P is cyclic: its first four differential rows are invertible.
    rows: list[sp.Matrix] = []
    row = sp.Matrix([[1, 0, 0, 0]])
    for _ in range(5):
        rows.append(row)
        row = _derivative_row(row, A4)
    observability = sp.Matrix.vstack(*rows[:4])
    expected_observability = _expr(
        data["carrier_cyclic_elimination"]["observability_determinant"]
    )
    _require(
        _zero(observability.det() - expected_observability),
        "P observability determinant drift",
    )
    _require(expected_observability != 0, "cyclic determinant vanished")

    # P'''' = c0 P + ... + c3 P'''; the monic scalar operator has -c_k.
    coefficients = (rows[4] * observability.inv()).applyfunc(_cancel)
    scalar = data["carrier_cyclic_elimination"]["scalar_operator"]
    expected_l4 = [
        _expr(scalar["D0"]),
        _expr(scalar["D1"]),
        _expr(scalar["D2"]),
        _expr(scalar["D3"]),
    ]
    derived_l4 = [_cancel(-coefficients[0, index]) for index in range(4)]
    _require(
        all(_zero(left - right) for left, right in zip(derived_l4, expected_l4)),
        "cyclic scalar order-four operator drift",
    )
    composed = _compose_second_order(a_x, b_x, a_rw, b_rw)
    _require(
        all(_zero(left - right) for left, right in zip(derived_l4, composed)),
        "L4 is not L_x composed with L_RW",
    )

    sequence = data["carrier_exact_sequence"]
    J = _matrix(sequence["RW_embedding_J"])
    K = _matrix(sequence["quotient_K"])
    N = _matrix(sequence["right_inverse_N"])
    T = sp.Matrix.hstack(J, N)
    _require(
        _matrix_zero(J.diff(R) + J * A_rw - A4 * J),
        "RW embedding is not a chain map",
    )
    _require(_matrix_zero(K * J), "quotient does not kill the RW submodule")
    _require(
        _matrix_zero(K.diff(R) + K * A4 - A_x * K),
        "L_x quotient is not a chain map",
    )
    _require(_matrix_equal(K * N, sp.eye(2)), "N is not a right inverse of K")
    _require(
        _zero(T.det() - _expr(sequence["gauge_determinant"])),
        "carrier triangular gauge determinant drift",
    )
    transformed = (T.inv() * (A4 * T - T.diff(R))).applyfunc(_cancel)
    _require(
        _matrix_equal(transformed, _matrix(sequence["transformed_A4"])),
        "transformed carrier connection drift",
    )
    expected_triangular = sp.zeros(4, 4)
    expected_triangular[:2, :2] = A_rw
    expected_triangular[2:, 2:] = A_x
    expected_triangular[1, 2] = 1
    _require(
        _matrix_equal(transformed, expected_triangular),
        "carrier did not reduce to the canonical L_x o L_RW companion",
    )
    _require(
        sequence["exact_sequence"] == "0 -> M_RW -> M_A4 -> M_x -> 0"
        and sequence["dimensions"] == [2, 4, 2],
        "carrier exact-sequence ledger drift",
    )

    # Independently identify the metric Einstein kernel with the same RW
    # companion through the standard axial master Psi=(B H1+H0)/r.
    kernel = data["Einstein_kernel_RW_equivalence"]
    U = _matrix(kernel["U_H1F_to_PsiPsiPrime"])
    _require(
        _zero(U.det() - _expr(kernel["U_determinant"])),
        "Einstein-kernel gauge determinant drift",
    )
    _require(
        _matrix_zero(U.diff(R) + U * kernel2 - A_rw * U),
        "Einstein kernel is not conjugate to L_RW",
    )
    h0 = _expr(complete["complete_reconstruction"]["H0_reconstruction"]).subs(
        {P: 0, PP: 0, Q: 0, QP: 0}
    )
    psi = _cancel(((1 - 2 / R) * H1 + h0) / R)
    psi_row = sp.Matrix([[sp.diff(psi, H1), sp.diff(psi, F)]])
    _require(
        _matrix_equal(psi_row, U[:1, :]),
        "displayed RW master map is not derived from H0,H1",
    )

    # The natural full triangular gauge still couples the Lx quotient into
    # the Einstein RW block.  This is the first obstruction to promoting the
    # filtration to a direct decomposition; it is not claimed gauge invariant.
    transformed_source = (U * source * T).applyfunc(_cancel)
    witness = transformed_source[0, 2]
    _require(
        _zero(
            witness
            - _expr(
                data["complete_six_state_filtration"][
                    "natural_gauge_Lx_to_metric_extension_witness"
                ]
            )
        ),
        "natural Lx-to-metric extension witness drift",
    )
    _require(witness != 0, "natural extension witness was erased")
    filtration = data["complete_six_state_filtration"]
    _require(
        filtration["diagonal_factor_order_after_reordering"]
        == [
            "L_RW Einstein metric kernel",
            "L_RW carrier submodule",
            "L_x carrier quotient",
        ]
        and filtration["dimensions"] == [2, 2, 2]
        and filtration["triangular_equivalent_certified"] is True,
        "complete factor filtration drift",
    )
    _require(
        filtration["stronger_direct_decomposition"] == "not established",
        "direct decomposition was silently promoted",
    )

    repeated = imports["repeated_factor_audit"]
    endpoint = data["endpoint_comparison"]
    _require(
        endpoint["carrier_horizon_multiset"]
        == repeated["endpoint_obstruction"]["Ricci_carrier_horizon_exponents"]
        and endpoint["carrier_infinity_rates"]
        == repeated["endpoint_obstruction"]["carrier_infinity_rates"],
        "endpoint multiplicity comparison drift",
    )
    witt = imports["endpoint_witt"]
    _require(
        endpoint["endpoint_Witt_split"]
        == witt["uniform_interval_conclusion"]["witt_decomposition"],
        "endpoint Witt comparison drift",
    )

    flags = data["claim_flags"]
    for proved in (
        "carrier_scalar_factorization_Lx_after_LRW_certified",
        "carrier_RW_submodule_certified",
        "carrier_Lx_quotient_certified",
        "Lx_spin_one_RW_gauge_certified",
        "Einstein_kernel_RW_equivalence_certified",
        "complete_RW_RW_Lx_triangular_filtration_certified",
    ):
        _require(flags[proved] is True, f"proved factor claim demoted: {proved}")
    for open_claim in (
        "complete_direct_RW_square_plus_Lx_decomposition_certified",
        "rational_extension_splitting_certified",
        "endpoint_Witt_vectors_assigned_to_operator_factors",
        "radial_or_time_Jordan_origin_certified",
    ):
        _require(flags[open_claim] is False, f"open claim promoted: {open_claim}")
    limits = set(data["does_not_establish"])
    _require(
        "a direct differential-module isomorphism M_Bach = ker(L_RW**2) direct_sum ker(L_x)"
        in limits
        and "a radial generalized-mode or time-translation Jordan interpretation"
        in limits
        and "an assignment of endpoint Witt vectors to the RW or L_x factors"
        in limits,
        "direct-sum/Jordan/endpoint boundary drift",
    )
    _require(
        "a physical Maxwell field, spin-one particle or reconstruction assignment for the L_x factor"
        in limits,
        "spin-one physical boundary drift",
    )


def verify() -> None:
    verify_certificate(json.loads(CERTIFICATE.read_text()))
    print("PASS exact axial RW/RW/Lx triangular factor preflight")


if __name__ == "__main__":
    verify()
