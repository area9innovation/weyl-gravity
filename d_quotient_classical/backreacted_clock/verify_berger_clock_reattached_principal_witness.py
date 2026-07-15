#!/usr/bin/env python3
"""Independent symbol consumer for the clock-reattached Berger witness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.verify_berger_retained_minimal_operator import (
        ALPHA_B,
        _load_matrix,
    )
except ModuleNotFoundError:  # Direct script execution.
    from verify_berger_retained_minimal_operator import ALPHA_B, _load_matrix


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS.json"
Q1_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CLOCK_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json"
PAIRS = tuple((first, second) for first in range(4) for second in range(first, 4))
ETA = sp.diag(-1, 1, 1, 1)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


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


def _full_gauge(momenta: tuple[sp.Symbol, ...]) -> sp.Matrix:
    gauge = sp.zeros(10, 5)
    # Column order: three spatial diffeomorphisms, temporal diffeomorphism,
    # Weyl.  This reconstruction does not import the producing script.
    for row, (first, second) in enumerate(PAIRS):
        for spatial in range(1, 4):
            gauge[row, spatial - 1] = (
                momenta[first] * (1 if second == spatial else 0)
                + momenta[second] * (1 if first == spatial else 0)
            )
        gauge[row, 3] = (
            (momenta[first] if second == 0 else 0)
            + (momenta[second] if first == 0 else 0)
        )
        gauge[row, 4] = 2 * ETA[first, second]
    return gauge


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text())
    q1 = json.loads(Q1_CERTIFICATE.read_text())
    assert payload["dependency_refs"]["retained_q1"]["sha256"] == _sha256(Q1_CERTIFICATE)
    assert payload["dependency_refs"]["clock_sdr"]["sha256"] == _sha256(CLOCK_CERTIFICATE)

    hessian4 = _symbol(_load_matrix(q1["q1_blocks"]["H_retained"]), 4)
    p = sp.symbols("p0:4")
    wave = -p[0] ** 2 + p[1] ** 2 + p[2] ** 2 + p[3] ** 2
    gauge = _full_gauge(p)
    trace = sp.Matrix([[ETA[first, second] for first, second in PAIRS]])

    divergence = sp.zeros(4, 10)
    for mu in range(4):
        for column, (first, second) in enumerate(PAIRS):
            divergence[mu, column] = sum(
                ETA[axis, axis] * p[axis]
                for axis in range(4)
                if tuple(sorted((axis, mu))) == (first, second)
            )
    double_divergence = sp.zeros(1, 10)
    for mu in range(4):
        double_divergence += ETA[mu, mu] * p[mu] * divergence[mu, :]

    companion = sp.zeros(5, 10)
    diffeomorphism = sp.zeros(4, 10)
    for mu in range(4):
        diffeomorphism[mu, :] = (
            wave * divergence[mu, :]
            - sp.Rational(1, 6) * wave * p[mu] * trace
            - sp.Rational(1, 3) * p[mu] * double_divergence
        )
    companion[:3, :] = diffeomorphism[1:4, :]
    companion[3, :] = diffeomorphism[0, :]
    companion[4, :] = (
        sp.Rational(1, 6) * wave**2 * trace
        - sp.Rational(1, 6) * wave * double_divergence
    )
    raised = sp.diag(
        *[
            sp.Rational(
                1,
                (1 if first == second else 2) * ETA[first, first] * ETA[second, second],
            )
            for first, second in PAIRS
        ]
    )
    fibre = sp.Rational(4, 1) / ALPHA_B * raised
    assert sp.simplify(fibre * hessian4 + gauge * companion - wave**2 * sp.eye(10)) == sp.zeros(10)
    assert sp.simplify(companion * gauge - wave**2 * sp.eye(5)) == sp.zeros(5)

    symbols = {"p0": p[0], "p1": p[1], "p2": p[2], "p3": p[3]}
    frozen_companion = sp.Matrix(
        [[sp.sympify(value, locals=symbols) for value in row] for row in payload["normalized_witness"]["companion_matrix"]]
    )
    assert sp.simplify(frozen_companion - companion) == sp.zeros(5, 10)
    flags = payload["flags"]
    assert flags["BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS"] is True
    assert flags["BERGER_FULL_METRIC_BIWAVE_PRINCIPAL"] is True
    assert flags["BERGER_FULL_GHOST_BIWAVE_PRINCIPAL"] is True
    assert flags["BERGER_CURVED_CLOCK_REATTACHED_WITNESS"] is False
    assert flags["BERGER_CAUSAL_GREEN_HOMOTOPY"] is False
    assert flags["BERGER_ARITY_TWO_D_CARTAN"] is False
    assert payload["next_gate"] == "BERGER_CURVED_CLOCK_REATTACHED_WITNESS"
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS_INDEPENDENT: PASS")
    print("metric (zeta^2)^2 I_10 and ghost (zeta^2)^2 I_5: PASS")
    print("curved lower-order witness and causal homotopy: OPEN")


if __name__ == "__main__":
    main()
