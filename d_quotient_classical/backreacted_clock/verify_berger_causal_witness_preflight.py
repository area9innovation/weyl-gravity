#!/usr/bin/env python3
"""Independent QW+WQ and endpoint check for the Berger causal preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.verify_berger_retained_minimal_operator import (
        ALPHA_B,
        U,
        V,
        _add,
        _load_matrix,
        _multiply,
    )
except ModuleNotFoundError:  # Direct script execution.
    from verify_berger_retained_minimal_operator import (
        ALPHA_B,
        U,
        V,
        _add,
        _load_matrix,
        _multiply,
    )


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_WITNESS_PREFLIGHT.json"
Q1_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
PAIRS = tuple((first, second) for first in range(4) for second in range(first, 4))
ETA = sp.diag(-1, 1, 1, 1)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _matrix_add(left, right):
    return [
        [_add(left[row][column], right[row][column]) for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def _identity(rank: int):
    return [
        [{(): sp.S.One} if row == column else {} for column in range(rank)]
        for row in range(rank)
    ]


def _symbol(matrix, order: int) -> sp.Matrix:
    momenta = sp.symbols("p0:4")
    return sp.Matrix(
        len(matrix),
        len(matrix[0]),
        lambda row, column: sp.factor(
            sum(
                coefficient * sp.prod(momenta[axis] for axis in word)
                for word, coefficient in matrix[row][column].items()
                if len(word) == order
            )
        ),
    )


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text())
    q1 = json.loads(Q1_CERTIFICATE.read_text())
    assert payload["q1_ref"]["sha256"] == _sha256(Q1_CERTIFICATE)
    assert q1["flags"]["BERGER_RETAINED_MINIMAL_OPERATOR"] is True

    qblocks = q1["q1_blocks"]
    gauge = _load_matrix(qblocks["K_spatial"])
    hessian = _load_matrix(qblocks["H_retained"])
    noether = _load_matrix(qblocks["minus_K_spatial_sharp"])
    witness = payload["witness_blocks"]
    companion = _load_matrix(witness["M_to_G"])
    middle = _load_matrix(witness["E_to_M"])
    companion_adjoint = _load_matrix(witness["I_to_E"])
    assert middle == _identity(10)

    expected = {
        "ghost": _multiply(companion, gauge),
        "metric": _matrix_add(hessian, _multiply(gauge, companion)),
        "metric_antifield": _matrix_add(hessian, _multiply(companion_adjoint, noether)),
        "identity": _multiply(noether, companion_adjoint),
    }
    for name, matrix in expected.items():
        assert matrix == _load_matrix(payload["degreewise_P_blocks"][name])

    p = sp.symbols("p0:4")
    q2 = -p[0] ** 2 + p[1] ** 2 + p[2] ** 2 + p[3] ** 2
    ghost4 = _symbol(expected["ghost"], 4)
    assert sp.simplify(ghost4 - ALPHA_B * q2**2 * sp.eye(3)) == sp.zeros(3)
    field4 = _symbol(expected["metric"], 4)
    fixture = {p[0]: 2, p[1]: 1, p[2]: 3, p[3]: 4, U: 1, V: 5, ALPHA_B: 7}
    assert field4.subs(fixture).rank() == 8

    k_temporal = sp.zeros(10, 1)
    metric_trace = sp.zeros(10, 1)
    k_spatial = _symbol(gauge, 1)
    for row, (first, second) in enumerate(PAIRS):
        k_temporal[row, 0] = (
            (p[first] if second == 0 else 0)
            + (p[second] if first == 0 else 0)
        )
        metric_trace[row, 0] = ETA[first, second]
    weyl_carrier = q2 * metric_trace + k_spatial * sp.Matrix(p[1:4])
    carriers = k_temporal.row_join(weyl_carrier)
    assert sp.simplify(field4 * carriers) == sp.zeros(10, 2)
    assert carriers.subs(fixture).rank() == 2

    flags = payload["flags"]
    assert flags["BERGER_GHOST_ENDPOINT_GREEN_HYPERBOLIC"] is True
    assert flags["BERGER_IDENTITY_ENDPOINT_GREEN_HYPERBOLIC"] is True
    assert flags["BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION"] is False
    assert flags["BERGER_CAUSAL_GREEN_HOMOTOPY"] is False
    assert flags["BERGER_ARITY_TWO_D_CARTAN"] is False
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_CAUSAL_WITNESS_PREFLIGHT_INDEPENDENT: PASS")
    print("QW+WQ blocks, endpoint biwave, and rank-eight-plus-two metric boundary: PASS")
    print("metric Green realization and total causal homotopy: OPEN")


if __name__ == "__main__":
    main()
