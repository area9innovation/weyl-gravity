#!/usr/bin/env python3
"""Independent verifier for the positive-mixed replacement unary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import generate_berger_global_detector_rods as rods
from closed_universe_observers import generate_berger_global_rod_q1_solvability as solve


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json"
X = P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement-112-positive-mixed-action-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_matrices() -> tuple[sp.Matrix, sp.Matrix]:
    sa, ca, su, cu = sp.symbols("sa ca su cu", nonzero=True, real=True)
    q = 3 * sp.sqrt(10) / 10
    profiles = (
        (-q * sa, 0, 0, q * ca),
        (0, 2 * ca, 2 * sa, 0),
        (0, -2 * sa, 2 * ca, 0),
        (-2 * q * sa * ca, 0, 0, q * (ca**2 - sa**2)),
        (0, 2 * (ca**2 - sa**2), 4 * sa * ca, 0),
        (0, -4 * sa * ca, 2 * (ca**2 - sa**2), 0),
    )
    current, derivative = [], []
    for index, profile in enumerate(profiles):
        cosine, sine = ((cu, su) if index < 3 else (cu**2 - su**2, 2 * su * cu))
        current.append([cosine * x for x in profile] + [sine * x for x in profile])
        derivative.append([sine * x for x in profile] + [-cosine * x for x in profile])
    current_matrix = sp.Matrix(current)
    derivative_matrix = sp.Matrix(derivative)
    basis = sp.Matrix.vstack(current_matrix, derivative_matrix[0, :], derivative_matrix[3, :])
    differentiated = sp.Matrix.vstack(derivative_matrix, -current_matrix[0, :], -current_matrix[3, :])
    return basis, differentiated


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    basis, differentiated = independent_matrices()
    inverse = basis.inv()
    kinetic = (inverse.T * inverse).applyfunc(sp.factor)
    generator = differentiated * inverse
    coefficient_generator = (inverse * differentiated).applyfunc(sp.factor)
    expected = sp.zeros(8)
    expected[:4, 4:] = -sp.eye(4)
    expected[4:, :4] = sp.eye(4)
    assert coefficient_generator == expected
    assert kinetic == kinetic.T
    assert (generator.T * kinetic + kinetic * generator).applyfunc(sp.factor) == sp.zeros(8)

    retained = json.loads((ROOT / cert["dependency_refs"]["retained_q1"]["path"]).read_text())["q1_blocks"]
    operator = solve._operator_matrix(retained["H_retained"], sp.S.Zero)
    noether = solve._operator_matrix(retained["minus_K_spatial_sharp"], sp.S.Zero)
    source = sp.zeros(100, 1)
    for index, value in payload["background_equation"]["source_sparse"]:
        source[index] = sp.sympify(value)
    primitive = sp.zeros(100, 1)
    for index, value in payload["background_equation"]["Phi2_sparse"]:
        primitive[index] = sp.sympify(value)
    assert noether * source == sp.zeros(30, 1)
    assert operator * primitive + source == sp.zeros(100, 1)
    assert payload["carrier"]["pairing_rank"] == 112
    assert payload["complete_unary"]["q1_squared_defect_count"] == 0
    assert payload["complete_unary"]["odd_cyclicity_defect_count"] == 0
    assert payload["leading_observer_map"]["response_rank"] == 2
    assert payload["leading_observer_map"]["survives_full_112_gauge_reduction"] == "NO_CERTIFIED_MAP"
    print("BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
