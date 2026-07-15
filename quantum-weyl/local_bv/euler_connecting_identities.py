"""Exact tensor-sector audit for the four-dimensional Euler connection rows.

The proof uses a coordinate frame only as a finite presentation of the
tensor identities.  It constructs exact bases of the algebraic Weyl tensor
and Cotton tensor in four dimensions, expands their differential forms, and
checks every independent reduced covariant curvature sector over ``Fraction``
arithmetic.  This deliberately stops before the inhomogeneous
``tilde_omega = U - P`` projection, so it is not by itself a certificate of
the two ordinary-bidegree connecting equations.  No random or floating-point
tensor sampling enters the audit.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
import json
from typing import Iterable, Sequence

from .algebra import canonical_sha256
from .quotient import exact_nullspace, exact_rank


DIMENSION = 4
PAIRS = tuple(combinations(range(DIMENSION), 2))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
WEYL_COORDINATES = tuple(
    (left, right)
    for left in range(len(PAIRS))
    for right in range(left, len(PAIRS))
)
WEYL_COORDINATE_INDEX = {
    coordinate: index for index, coordinate in enumerate(WEYL_COORDINATES)
}
COTTON_COORDINATES = tuple(
    (first, pair) for first in range(DIMENSION) for pair in range(len(PAIRS))
)
COTTON_COORDINATE_INDEX = {
    coordinate: index for index, coordinate in enumerate(COTTON_COORDINATES)
}


def _oriented_pair(left: int, right: int) -> tuple[int | None, int]:
    if left == right:
        return None, 0
    if left < right:
        return PAIR_INDEX[(left, right)], 1
    return PAIR_INDEX[(right, left)], -1


def _weyl_constraint(
    terms: Iterable[tuple[int, tuple[int, int, int, int]]],
) -> tuple[Fraction, ...]:
    row = [Fraction() for _ in WEYL_COORDINATES]
    for coefficient, (a, b, c, d) in terms:
        left, left_sign = _oriented_pair(a, b)
        right, right_sign = _oriented_pair(c, d)
        if left is None or right is None:
            continue
        pair = tuple(sorted((left, right)))
        row[WEYL_COORDINATE_INDEX[pair]] += coefficient * left_sign * right_sign
    return tuple(row)


def _cotton_constraint(
    terms: Iterable[tuple[int, tuple[int, int, int]]],
) -> tuple[Fraction, ...]:
    row = [Fraction() for _ in COTTON_COORDINATES]
    for coefficient, (a, b, c) in terms:
        pair, sign = _oriented_pair(b, c)
        if pair is not None:
            row[COTTON_COORDINATE_INDEX[(a, pair)]] += coefficient * sign
    return tuple(row)


@lru_cache(maxsize=1)
def _weyl_constraints() -> tuple[tuple[Fraction, ...], ...]:
    constraints = [
        _weyl_constraint(
            (
                (1, (0, 1, 2, 3)),
                (1, (0, 2, 3, 1)),
                (1, (0, 3, 1, 2)),
            )
        )
    ]
    constraints.extend(
        _weyl_constraint((1, (a, b, a, d)) for a in range(DIMENSION))
        for b in range(DIMENSION)
        for d in range(b, DIMENSION)
    )
    return tuple(constraints)


@lru_cache(maxsize=1)
def _weyl_basis() -> tuple[tuple[Fraction, ...], ...]:
    basis = exact_nullspace(
        _weyl_constraints(), column_count=len(WEYL_COORDINATES)
    )
    if len(basis) != 10:
        raise AssertionError("four-dimensional algebraic Weyl dimension drifted")
    return basis


@lru_cache(maxsize=1)
def _cotton_constraints() -> tuple[tuple[Fraction, ...], ...]:
    constraints = [
        _cotton_constraint(
            ((1, (a, b, c)), (1, (b, c, a)), (1, (c, a, b)))
        )
        for a, b, c in combinations(range(DIMENSION), 3)
    ]
    constraints.extend(
        _cotton_constraint((1, (a, a, c)) for a in range(DIMENSION))
        for c in range(DIMENSION)
    )
    return tuple(constraints)


@lru_cache(maxsize=1)
def _cotton_basis() -> tuple[tuple[Fraction, ...], ...]:
    basis = exact_nullspace(
        _cotton_constraints(), column_count=len(COTTON_COORDINATES)
    )
    if len(basis) != 16:
        raise AssertionError("four-dimensional irreducible Cotton dimension drifted")
    return basis


# Exterior generators are omega, t_0,...,t_3, dx^0,...,dx^3.  A bit mask is
# therefore a canonical exterior monomial; its coefficient is exact rational.
ExteriorExpression = dict[int, Fraction]
ONE: ExteriorExpression = {0: Fraction(1)}


def _atom(position: int) -> ExteriorExpression:
    return {1 << position: Fraction(1)}


OMEGA = _atom(0)
TILDE = tuple(_atom(1 + index) for index in range(DIMENSION))
DX = tuple(_atom(1 + DIMENSION + index) for index in range(DIMENSION))


def _wedge_pair(left: ExteriorExpression, right: ExteriorExpression) -> ExteriorExpression:
    output: ExteriorExpression = {}
    for left_mask, left_coefficient in left.items():
        for right_mask, right_coefficient in right.items():
            if left_mask & right_mask:
                continue
            inversions = sum(
                1
                for left_index in range(1 + 2 * DIMENSION)
                if left_mask & (1 << left_index)
                for right_index in range(1 + 2 * DIMENSION)
                if right_mask & (1 << right_index) and left_index > right_index
            )
            mask = left_mask | right_mask
            coefficient = left_coefficient * right_coefficient
            if inversions % 2:
                coefficient = -coefficient
            output[mask] = output.get(mask, Fraction()) + coefficient
    return {mask: coefficient for mask, coefficient in output.items() if coefficient}


def _wedge(*factors: ExteriorExpression) -> ExteriorExpression:
    output = ONE
    for factor in factors:
        output = _wedge_pair(output, factor)
    return output


def _sum(*expressions: ExteriorExpression) -> ExteriorExpression:
    output: ExteriorExpression = {}
    for expression in expressions:
        for mask, coefficient in expression.items():
            output[mask] = output.get(mask, Fraction()) + coefficient
    return {mask: coefficient for mask, coefficient in output.items() if coefficient}


def _scale(coefficient: Fraction | int, expression: ExteriorExpression) -> ExteriorExpression:
    coefficient = Fraction(coefficient)
    return {
        mask: coefficient * value
        for mask, value in expression.items()
        if coefficient * value
    }


def _epsilon(indices: Sequence[int]) -> int:
    if len(set(indices)) != DIMENSION:
        return 0
    inversions = sum(
        indices[left] > indices[right]
        for left in range(DIMENSION)
        for right in range(left + 1, DIMENSION)
    )
    return -1 if inversions % 2 else 1


def _weyl_value(
    vector: Sequence[Fraction], a: int, b: int, c: int, d: int
) -> Fraction:
    left, left_sign = _oriented_pair(a, b)
    right, right_sign = _oriented_pair(c, d)
    if left is None or right is None:
        return Fraction()
    coordinate = tuple(sorted((left, right)))
    return left_sign * right_sign * vector[WEYL_COORDINATE_INDEX[coordinate]]


def _cotton_value(
    vector: Sequence[Fraction], a: int, b: int, c: int
) -> Fraction:
    pair, sign = _oriented_pair(b, c)
    if pair is None:
        return Fraction()
    return sign * vector[COTTON_COORDINATE_INDEX[(a, pair)]]


def _weyl_form(vector: Sequence[Fraction], a: int, b: int) -> ExteriorExpression:
    return _sum(
        *(
            _scale(_weyl_value(vector, a, b, c, d), _wedge(DX[c], DX[d]))
            for c, d in PAIRS
        )
    )


def _cotton_form(vector: Sequence[Fraction], a: int) -> ExteriorExpression:
    return _sum(
        *(
            _scale(_cotton_value(vector, a, b, c), _wedge(DX[b], DX[c]))
            for b, c in PAIRS
        )
    )


def _d_omega() -> ExteriorExpression:
    return _sum(*(_wedge(DX[index], TILDE[index]) for index in range(DIMENSION)))


def _d_weyl_form(cotton: Sequence[Fraction], a: int, b: int) -> ExteriorExpression:
    """Use D W^(ab) = C^a wedge dx^b - C^b wedge dx^a."""

    return _sum(
        _wedge(_cotton_form(cotton, a), DX[b]),
        _scale(-1, _wedge(_cotton_form(cotton, b), DX[a])),
    )


def _d_phi1_sectors(
    weyl: Sequence[Fraction], cotton: Sequence[Fraction]
) -> tuple[ExteriorExpression, ExteriorExpression, ExteriorExpression]:
    d_omega_terms: list[ExteriorExpression] = []
    d_tilde_terms: list[ExteriorExpression] = []
    d_weyl_terms: list[ExteriorExpression] = []
    for a, nu, mu1, mu2 in permutations(range(DIMENSION)):
        coefficient = -4 * _epsilon((a, nu, mu1, mu2))
        weyl_form = _weyl_form(weyl, mu1, mu2)
        d_omega_terms.append(
            _scale(coefficient, _wedge(_d_omega(), TILDE[a], DX[nu], weyl_form))
        )
        d_tilde_terms.append(
            _scale(
                -coefficient,
                _wedge(OMEGA, _cotton_form(cotton, a), DX[nu], weyl_form),
            )
        )
        d_weyl_terms.append(
            _scale(
                -coefficient,
                _wedge(OMEGA, TILDE[a], DX[nu], _d_weyl_form(cotton, mu1, mu2)),
            )
        )
    return _sum(*d_omega_terms), _sum(*d_tilde_terms), _sum(*d_weyl_terms)


def _d_phi2_sectors(
    cotton: Sequence[Fraction],
) -> tuple[ExteriorExpression, ExteriorExpression]:
    d_omega_terms: list[ExteriorExpression] = []
    d_tilde_terms: list[ExteriorExpression] = []
    for a, b, nu1, nu2 in permutations(range(DIMENSION)):
        coefficient = 4 * _epsilon((a, b, nu1, nu2))
        d_omega_terms.append(
            _scale(
                coefficient,
                _wedge(_d_omega(), TILDE[a], TILDE[b], DX[nu1], DX[nu2]),
            )
        )
        d_tilde_terms.extend(
            (
                _scale(
                    -coefficient,
                    _wedge(OMEGA, _cotton_form(cotton, a), TILDE[b], DX[nu1], DX[nu2]),
                ),
                _scale(
                    coefficient,
                    _wedge(OMEGA, TILDE[a], _cotton_form(cotton, b), DX[nu1], DX[nu2]),
                ),
            )
        )
    return _sum(*d_omega_terms), _sum(*d_tilde_terms)


def _build_euler_connecting_identity_analysis() -> dict[str, object]:
    """Verify the exact reduced covariant sectors entering D(Phi_1 + Phi_2)."""

    weyl_basis = _weyl_basis()
    cotton_basis = _cotton_basis()
    zero_weyl = (Fraction(),) * len(WEYL_COORDINATES)
    zero_cotton = (Fraction(),) * len(COTTON_COORDINATES)

    phi1_domega = [_d_phi1_sectors(weyl, zero_cotton)[0] for weyl in weyl_basis]
    phi1_dtilde = [
        _d_phi1_sectors(weyl, cotton)[1]
        for weyl in weyl_basis
        for cotton in cotton_basis
    ]
    phi2_domega = _d_phi2_sectors(zero_cotton)[0]
    cotton_connecting = [
        _sum(
            _d_phi1_sectors(zero_weyl, cotton)[2],
            _d_phi2_sectors(cotton)[1],
        )
        for cotton in cotton_basis
    ]

    sectors = {
        "Domega_Phi1_linear_W": phi1_domega,
        "Dtilde_Phi1_bilinear_W_Cotton": phi1_dtilde,
        "Domega_Phi2_dimension_identity": [phi2_domega],
        "DW_Phi1_plus_Dtilde_Phi2": cotton_connecting,
    }
    residual_counts = {
        name: sum(bool(residual) for residual in residuals)
        for name, residuals in sectors.items()
    }
    if any(residual_counts.values()):
        raise AssertionError(f"Euler connecting residuals remain: {residual_counts}")

    payload = {
        "result_id": "EULER_CONNECTING_TENSOR_SECTOR_AUDIT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dimension": DIMENSION,
        "arithmetic": "EXACT_RATIONAL",
        "weyl_basis_dimension": len(weyl_basis),
        "cotton_basis_dimension": len(cotton_basis),
        "constraint_rank_receipt": {
            "weyl_coordinate_dimension": len(WEYL_COORDINATES),
            "weyl_constraint_row_count": len(_weyl_constraints()),
            "weyl_constraint_rank": exact_rank(_weyl_constraints()),
            "cotton_coordinate_dimension": len(COTTON_COORDINATES),
            "cotton_constraint_row_count": len(_cotton_constraints()),
            "cotton_constraint_rank": exact_rank(_cotton_constraints()),
        },
        "basis_constraints": {
            "weyl": "pair antisymmetry, pair exchange, algebraic Bianchi, tracefree",
            "cotton": "last-pair antisymmetry, cyclic identity, tracefree",
        },
        "source_project_cotton_bridge": "C_source = -A_project",
        "horizontal_rows": {
            "D_omega": "dx^mu tilde_omega_mu",
            "D_tilde_omega_alpha": "C_source_alpha",
            "D_W_ab": "C_source^a wedge dx^b - C_source^b wedge dx^a",
        },
        "sector_case_counts": {
            name: len(residuals) for name, residuals in sectors.items()
        },
        "sector_nonzero_residual_counts": residual_counts,
        "checks": {
            "weyl_tensor_space_exhaustive": "VERIFIED_DIMENSION_10",
            "cotton_tensor_space_exhaustive": "VERIFIED_DIMENSION_16",
            "constraint_ranks_exact": "VERIFIED",
            "Domega_Phi1": "VERIFIED",
            "Dtilde_Phi1": "VERIFIED",
            "Domega_Phi2": "VERIFIED",
            "DW_Phi1_plus_Dtilde_Phi2": "VERIFIED",
            "reduced_covariant_total_form_sectors": "VERIFIED",
            "ordinary_bidegree_projection": "NOT_COMPUTED",
            "Gamma_action_and_homogeneous_weight_rows": "NOT_COMPUTED",
        },
        "claim_boundary": {
            "tensor_sector_status": "REDUCED_COVARIANT_SECTORS_VERIFIED",
            "full_total_form_connecting_identity": "NOT_COMPUTED",
            "ordinary_bidegree_connecting_equations": "PENDING_COMPONENT_PROJECTION",
            "relative_cohomology_status": "UNDECIDED",
        },
    }
    return {**payload, "analysis_sha256": canonical_sha256(payload)}


@lru_cache(maxsize=1)
def _cached_analysis_json() -> str:
    return json.dumps(
        _build_euler_connecting_identity_analysis(),
        sort_keys=True,
        separators=(",", ":"),
    )


def euler_connecting_identity_analysis() -> dict[str, object]:
    """Return a fresh copy of the cached exact tensor-sector audit."""

    return json.loads(_cached_analysis_json())
