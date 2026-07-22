"""Assemble the exact polar dangerous-layer current filtration.

The entry producers clear a factorized denominator
``D_left*conjugate(D_right)``.  Consequently the matrix of cleared
numerators has the same rank as the physical current matrix.  This module
works entirely over ``QQ(i)[Lambda,omega]`` and records the leading radical
and its induced next-layer form without factoring lift-dependent entries.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.polys.domains import QQ_I

PKG = Path(__file__).resolve().parent
ARTIFACTS = PKG / "current_artifacts"
OUT = ARTIFACTS / "oscillatory-matrix-filtration.json"
NAMES = ("E", "X0", "X1", "X2")
LAMBDA, OMEGA = sp.symbols("Lambda omega", real=True)


def zero() -> sp.Poly:
    return sp.Poly(0, LAMBDA, OMEGA, domain=QQ_I)


def conjugate(poly: sp.Poly) -> sp.Poly:
    expr = sp.conjugate(poly.as_expr()).subs(
        {sp.conjugate(LAMBDA): LAMBDA, sp.conjugate(OMEGA): OMEGA}
    )
    return sp.Poly(sp.expand(expr), LAMBDA, OMEGA, domain=QQ_I)


def load_entry(left: str, right: str, power: int) -> sp.Poly:
    data = json.loads((ARTIFACTS / f"oscillatory-{left}-{right}.json").read_text())
    layer = data["result"]["layers"].get(str(power))
    if layer is None:
        return zero()
    terms = {
        tuple(monomial): sp.sympify(coefficient, locals={"I": sp.I})
        for monomial, coefficient in layer["sparse_terms"]
    }
    return sp.Poly.from_dict(terms, (LAMBDA, OMEGA), domain=QQ_I)


def det3(matrix: list[list[sp.Poly]]) -> sp.Poly:
    a = matrix
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )


def adjugate3(matrix: list[list[sp.Poly]]) -> list[list[sp.Poly]]:
    a = matrix
    return [
        [
            a[(j + 1) % 3][(i + 1) % 3] * a[(j + 2) % 3][(i + 2) % 3]
            - a[(j + 1) % 3][(i + 2) % 3] * a[(j + 2) % 3][(i + 1) % 3]
            for j in range(3)
        ]
        for i in range(3)
    ]


def sparse(poly: sp.Poly) -> dict[str, object]:
    rows = [[list(monomial), sp.sstr(coefficient)] for monomial, coefficient in sorted(poly.terms())]
    blob = json.dumps(rows, separators=(",", ":")).encode()
    return {
        "term_count": len(rows),
        "total_degree": poly.total_degree() if rows else None,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "terms": rows,
    }


def input_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    leading = [[load_entry(a, b, 0) for b in NAMES] for a in NAMES]
    subleading = [[load_entry(a, b, -1) for b in NAMES] for a in NAMES]
    first_finite = [[load_entry(a, b, -2) for b in NAMES] for a in NAMES]
    anti_leading = all(
        (leading[i][j] + conjugate(leading[j][i])).is_zero
        for i in range(4)
        for j in range(4)
    )
    anti_subleading = all(
        (subleading[i][j] + conjugate(subleading[j][i])).is_zero
        for i in range(4)
        for j in range(4)
    )
    anti_first_finite = all(
        (first_finite[i][j] + conjugate(first_finite[j][i])).is_zero
        for i in range(4)
        for j in range(4)
    )
    if not anti_leading or not anti_subleading or not anti_first_finite:
        raise RuntimeError("dangerous-layer current matrix is not anti-Hermitian")

    extra = [row[1:] for row in leading[1:]]
    determinant = det3(extra)
    adjugate = adjugate3(extra)
    lower_cross = [leading[i][0] for i in range(1, 4)]
    upper_cross = leading[0][1:]
    tail = [
        -sum((adjugate[i][j] * lower_cross[j] for j in range(3)), zero())
        for i in range(3)
    ]
    radical = [determinant, *tail]
    schur_numerator = sum(
        (upper_cross[j] * (-tail[j]) for j in range(3)), zero()
    )
    null_checks = [
        sum((leading[i][j] * radical[j] for j in range(4)), zero())
        for i in range(4)
    ]
    induced_subleading = sum(
        (
            conjugate(radical[i]) * subleading[i][j] * radical[j]
            for i in range(4)
            for j in range(4)
        ),
        zero(),
    )
    induced_first_finite = sum(
        (
            conjugate(radical[i]) * first_finite[i][j] * radical[j]
            for i in range(4)
            for j in range(4)
        ),
        zero(),
    )
    if not schur_numerator.is_zero:
        raise RuntimeError("leading Schur numerator did not cancel")
    if not all(value.is_zero for value in null_checks):
        raise RuntimeError("reported leading radical is not null")
    if not induced_subleading.is_zero:
        raise RuntimeError("p=-1 form lifts the leading radical")

    coefficient, factors = sp.factor_list(determinant.as_expr())
    if len(factors) != 5:
        raise RuntimeError("unexpected determinant factorization")
    factor_records = []
    for factor, multiplicity in factors:
        factor_poly = sp.Poly(factor, LAMBDA, OMEGA, domain=QQ_I)
        factor_records.append(
            {"multiplicity": int(multiplicity), "polynomial": sparse(factor_poly)}
        )

    probe = {LAMBDA: sp.Integer(6), OMEGA: sp.Rational(3, 5)}
    source_paths = [
        ARTIFACTS / f"oscillatory-{left}-{right}.json"
        for left in NAMES
        for right in NAMES
    ]
    output = {
        "schema_version": "polar-current-filtration-v1",
        "basis": list(NAMES),
        "normalization": {
            "entry_rule": "G_p[i,j]=N_p[i,j]/(D_i*conjugate(D_j))",
            "rank_equivalence": "rank(G_p)=rank(N_p) away from reconstruction denominator poles",
            "determinant_rule": "det(K_actual)=det(K_N)/(product_i D_i*product_i conjugate(D_i))",
        },
        "input_artifact_hashes": {
            path.name: input_hash(path) for path in source_paths
        },
        "anti_hermitian": {"p0": anti_leading, "p_minus_1": anti_subleading, "p_minus_2": anti_first_finite},
        "leading_p0": {
            "extra_block_determinant": sparse(determinant),
            "extra_block_determinant_probe_Lambda6_omega3_over_5": sp.sstr(
                determinant.eval(probe)
            ),
            "factorization": {
                "coefficient": sp.sstr(coefficient),
                "factors": factor_records,
                "canonical_pivot_wall_status": "CLOSED_BY_CANONICAL_PIVOT_WALL_CERTIFICATE",
            },
            "schur_numerator_identically_zero": schur_numerator.is_zero,
            "generic_rank_away_from_detK_walls": 3,
            "generic_radical_dimension_away_from_detK_walls": 1,
            "normalized_radical": [sparse(value) for value in radical],
            "radical_identity_N0_y_zero": [value.is_zero for value in null_checks],
        },
        "subleading_p_minus_1": {
            "induced_form_on_leading_radical_identically_zero": induced_subleading.is_zero,
            "dangerous_filtration_disposition": "ONE_DIMENSIONAL_MIXED_RADICAL_SURVIVES_THROUGH_P_MINUS_1_AWAY_FROM_DETK_WALLS",
        },
        "first_finite_p_minus_2": {
            "induced_form_on_filtered_line": sparse(induced_first_finite),
            "identically_zero": induced_first_finite.is_zero,
            "disposition": "NONRADICAL_IF_COEFFICIENT_NONZERO" if not induced_first_finite.is_zero else "RADICAL_THROUGH_P_MINUS_2",
        },
        "claim_boundary": [
            "formal all-ell polar radial infinity module",
            "real nonzero omega and Lambda=ell(ell+1), ell>=2",
            "the chosen extra-complement detK is lift-sensitive; the separate wall certificate proves it nonzero on the physical domain",
            "horizon matching and global scattering are not established",
        ],
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
