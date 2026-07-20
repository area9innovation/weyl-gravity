#!/usr/bin/env python3
"""Independent verifier for the replacement 112-row K obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = (
    P
    / "certificates/"
    "BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_OBSTRUCTION.json"
)
X = (
    P
    / "certificates/"
    "BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_PAYLOAD.json"
)
SCHEMA = (
    P
    / "schema/"
    "berger-replacement-112-unary-theory-k-equivariance-obstruction-v1.schema.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_mod_unit_circles(
    expression: sp.Expr,
    *,
    sa: sp.Symbol,
    ca: sp.Symbol,
    su: sp.Symbol,
    cu: sp.Symbol,
) -> bool:
    numerator, _ = sp.together(expression).as_numer_denom()
    ideal = sp.groebner(
        [ca**2 + sa**2 - 1, cu**2 + su**2 - 1],
        ca,
        cu,
        sa,
        su,
        order="lex",
    )
    return sp.expand(ideal.reduce(sp.expand(numerator))[1]) == 0


def independent_matrices() -> tuple[sp.Matrix, sp.Matrix]:
    sa, ca, su, cu = sp.symbols("sa ca su cu", nonzero=True, real=True)
    q = 3 * sp.sqrt(10) / 10
    spatial = (
        (-q * sa, 0, 0, q * ca),
        (0, 2 * ca, 2 * sa, 0),
        (0, -2 * sa, 2 * ca, 0),
        (-2 * q * sa * ca, 0, 0, q * (ca**2 - sa**2)),
        (0, 2 * (ca**2 - sa**2), 4 * sa * ca, 0),
        (0, -4 * sa * ca, 2 * (ca**2 - sa**2), 0),
    )
    rows, time_derivatives = [], []
    for index, profile in enumerate(spatial):
        cosine, sine = (
            (cu, su)
            if index < 3
            else (cu**2 - su**2, 2 * su * cu)
        )
        rows.append(
            [cosine * value for value in profile]
            + [sine * value for value in profile]
        )
        time_derivatives.append(
            [sine * value for value in profile]
            + [-cosine * value for value in profile]
        )
    old = sp.Matrix(rows)
    deriv = sp.Matrix(time_derivatives)
    basis = sp.Matrix.vstack(old, deriv[0, :], deriv[3, :])
    differentiated = sp.Matrix.vstack(deriv, -old[0, :], -old[3, :])
    return basis, differentiated


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    basis, differentiated = independent_matrices()
    sa, ca, su, cu = sp.symbols("sa ca su cu", nonzero=True, real=True)
    determinant = sp.factor(basis.det())
    assert determinant == (
        sp.Rational(324, 25)
        * sa**2
        * su**2
        * (ca**2 + sa**2) ** 5
        * (cu**2 + su**2) ** 5
    )
    generator = differentiated * basis.inv()
    symmetric = (generator + generator.T).applyfunc(sp.factor)
    expected = sp.zeros(8)
    for index, sign in ((1, 1), (2, 1), (4, -1), (5, -1)):
        expected[index, index] = sign * 2 * cu / su
    for residual in symmetric - expected:
        assert zero_mod_unit_circles(
            residual, sa=sa, ca=ca, su=su, cu=cu
        )
    symmetric = expected
    assert symmetric.rank() == 4

    # The cotangent lift of A is -A^T, so the identity wave Hessian has
    # normalized commutator -(A^T+A).
    assert (-symmetric).rank() == 4
    skew = (generator - generator.T) / 2
    for residual in skew * basis - differentiated + symmetric * basis / 2:
        assert zero_mod_unit_circles(
            residual, sa=sa, ca=ca, su=su, cu=cu
        )
    assert basis[:-1, :].rank() == 7
    assert sp.Matrix.vstack(basis[:6, :], basis[7, :]).rank() == 7

    inverse = basis.inv()
    kinetic = inverse.T * inverse
    # This identity is algebraic and avoids heuristic simplification:
    # A=BJB^-1 and H=B^-T B^-1.
    complex_structure = inverse * differentiated
    for residual in complex_structure + complex_structure.T:
        assert zero_mod_unit_circles(
            residual, sa=sa, ca=ca, su=su, cu=cu
        )
    for residual in generator.T * kinetic + kinetic * generator:
        assert zero_mod_unit_circles(
            residual, sa=sa, ca=ca, su=su, cu=cu
        )

    first = payload["first_obstruction"]
    assert first["principal_commutator_rank"] == 4
    assert payload["disposition"]["complete_112_row_q1"] == "NO_CERTIFIED_MAP"
    assert payload["disposition"]["identity_kinetic_K_equivariance"] == (
        "OBSTRUCTED"
    )
    print(
        "BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_OBSTRUCTION "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
